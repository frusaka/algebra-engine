from __future__ import annotations
from itertools import filterfalse
from typing import Sequence


from .eval_trace import *

from datatypes.var import Var
from .utils import next_eqn
from utils.print_ import print_system


def _solve(eqns, org, v, seen):
    eqn = org[v]
    if eqn.__class__ is not System and eqn.left != v:
        raise ArithmeticError(f"Could not solve for {v}")
    eqns.remove(org)
    if eqn.__class__ is System:
        seen.update(eqn)
        ETSteps.register(ETSubNode(v, ETBranchNode(i.right for i in eqn)))
        new_eqns = []
        for i in eqn:
            j = [j.ast_subs({v: i.right}) for j in eqns]
            for idx in range(len(eqns)):
                if eqns[idx] in seen:
                    seen.add(j[idx])
            seen.add(i)
            new_eqns.append(System(j + [i]))

        if len(new_eqns) == 1:
            return list(new_eqns[0])
        return new_eqns
    seen.add(eqn)
    # Need a check for infinite solutions
    if eqn.left != v:
        raise ArithmeticError(f"Could not solve for {v}")

    # Substitute in the rest of equations
    ETSteps.register(ETSubNode(v, eqn.right))
    for i in range(len(eqns)):
        was_seen = eqns[i] in seen
        eqns[i] = eqns[i].ast_subs({v: eqn.right})
        if was_seen:
            seen.add(eqns[i])

    # Put the newly solved equation at the end
    eqns.append(eqn)
    return eqns


def _branched_solve(vals, eqns, seen):
    _, v = next_eqn(filterfalse(seen.__contains__, eqns[0]), vals)
    ETSteps.register(ETTextNode(f"Solve for {v}"))

    with ETSteps.branching(len(eqns)) as branches:
        for idx in branches:
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            ETSteps.register(ETNode(eqns[idx]))
            data = list(eqns[idx])
            eqn, _ = next_eqn(filterfalse(seen.__contains__, data), [v])
            eqns[idx] = System(_solve(data, eqn, v, seen))
            ETSteps.register(ETBranchNode(eqns[idx]))

    # Flatten when necessary (most cases)
    if next(iter(eqns[0])).__class__ is System:
        eqns[:] = list(j for i in eqns for j in i)
    ETSteps.register(ETBranchNode(eqns))
    vals.remove(v)


def _foreach_solve(eqns, value):
    ETSteps.register(ETBranchNode(eqns))
    if not any(eqn.left != value for eqn in eqns):
        return eqns
    # Expanded during the solving process
    sols = []
    with ETSteps.branching(len(eqns)) as branches:
        for idx, eqn in zip(branches, eqns):
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            try:
                res = eqn[value]
            except ArithmeticError:
                continue
            if res.__class__ is System:
                sols.extend(res)
            else:
                sols.append(res)
    return sols


class System(frozenset):
    """A system of equations"""

    def __getitem__(self, vals: Sequence[Var]) -> System:
        """Solve for a system of (in)equalities"""

        if vals.__class__ is Var:
            return System(_foreach_solve(self, vals))

        ETSteps.register(ETTextNode("Solving for " + str(vals)[1:-1]))
        ETSteps.register(ETNode(self))
        vals = set(vals)
        eqns = list(self)
        seen = set()
        # Solve for each variable separately
        with ETSteps.branching(len(vals)) as branches:
            for _ in branches:
                # Branched solving: previous variable had multiple solutions
                if eqns[0].__class__ is System:
                    _branched_solve(vals, eqns, seen)
                    continue
                # Chose the easiest variable to isolate
                eqn, v = next_eqn(filterfalse(seen.__contains__, eqns), vals)
                ETSteps.register(ETTextNode(f"Solve for {v}"))
                eqns = _solve(eqns, eqn, v, seen)
                if eqns[0].__class__ is System:
                    ETSteps.register(ETBranchNode(eqns))
                else:
                    ETSteps.register(ETNode(System(eqns)))
                vals.remove(v)
        return System(eqns)

    def __bool__(self) -> bool:
        return all(self)

    def __repr__(self) -> str:
        lpad = max(len(str(eqn.left)) for eqn in self)
        rpad = max(len(str(eqn.right)) for eqn in self)
        return print_system(
            [
                " " * (lpad - len(str(eqn.left)))
                + str(eqn)
                + " " * (rpad - len(str(eqn.right)))
                for eqn in sorted(self, key=lambda eqn: str(eqn.left))
            ]
        )

    def approx(self, threshold: float = 1e-10):
        return all(eqn.approx(threshold) for eqn in self)

    def expand(self):
        return System(i.expand() for i in self)

    def ast_subs(self, mapping: dict) -> System:
        return System(i.ast_subs(mapping) for i in self)

    def totex(self, align: bool = True) -> str:
        return "&" * align + "\\\\".join(map(lambda x: x.totex(align), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self) -> System:
        return System(i.normalize() for i in self)


__all__ = ["System"]
