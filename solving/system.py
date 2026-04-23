from __future__ import annotations

from copy import copy
from itertools import chain
from typing import Sequence


from datatypes.base import Node
from utils import steps
from utils.steps import *


from datatypes import *
from .utils import arrange_eqns, compute_grobner, next_eqn
from utils.print_ import print_system


def _solve(eqns: set, org, v, sols):
    inner = []
    with steps.scoped(inner):
        eqn = org.solve_for(v)
    steps.register(Step("", ETOperator("SOLVE", (org, v), eqn), inner))
    eqns.remove(org)
    if eqn.__class__ is System:
        new_eqns = []
        inner = []
        with steps.scoped(inner):
            for i in eqn:
                if i.left != v:
                    continue
                new_eqns.append(
                    (
                        System([j.subs({v: i.right}) for j in sols] + [copy(i)]),
                        {j.subs({v: i.right}) for j in eqns},
                    )
                )
                [steps.register(i) for i in chain(*new_eqns[-1])]
        if len(new_eqns) == 1:
            new_eqns = list(new_eqns[0])
        sols[:] = new_eqns
        res = ETBranch(i.right for i in eqn)
        steps.register(
            Step(
                "",
                ETOperator(
                    "SUBS",
                    (v, res),
                    ETBranch(System(chain(*i)) for i in sols),
                    force_keep=True,
                ),
                inner,
            )
        )
        return
    # Need a check for infinite solutions
    if eqn.left != v:
        raise ArithmeticError(f"Could not solve for {v}")
    # Substitute in the rest of equations
    inner = []
    mapping = {v: copy(eqn.right)}
    with steps.scoped(inner):
        for i in range(len(sols)):
            sols[i] = sols[i].subs(mapping)
            steps.register(sols[i])
        for j in eqns.copy():
            eqns.remove(j)
            j = j.subs(mapping)
            eqns.add(j)
            steps.register(j)
    # # Put the newly solved equation at the end
    sols.append(eqn)
    steps.register(
        Step(
            "",
            ETOperator("SUBS", (v, eqn.right), System([*eqns, *sols]), force_keep=True),
            inner,
        )
    )


def _branched_solve(vals, sols):
    _, v = next_eqn(sols[0][1], vals)

    with steps.scoped(branches := []):
        for idx in range(len(sols)):
            data, eqns = sols[idx]
            data = list(data)
            eqn, _ = next_eqn(eqns, [v])
            if eqn.left == v:
                data.append(eqn)
                eqns.remove(eqn)
                sols[idx] = System(data), eqns
                continue

            _solve(eqns, eqn, v, data)
            if data[0].__class__ is tuple:
                sols.extend(data)
                sols[idx] = None
            else:
                sols[idx] = System(data), eqns
    # Flattening in case of double multiple solutions
    while True:
        for idx in range(len(sols)):
            if sols[idx] is None:
                sols.pop(idx)
                break
        else:
            break

    vals.remove(v)
    steps.register(
        Step(
            f"Branch out",
            ETBranch(System({*i[0], *i[1]}) for i in sols),
            branches,
        )
    )


def _foreach_solve(eqns, value):
    if not any(eqn.left != value for eqn in eqns):
        return eqns
    # Branched during the solving process
    sols = []
    for idx, eqn in zip(range(1, len(eqns) + 1), eqns):
        inner = []
        try:
            with steps.scoped(inner):
                res = eqn.solve_for(value)
        except ArithmeticError as err:
            steps.register(Step(repr(err), "", ""))
            continue
        steps.register(Step(f"Branch {idx}", ETNode(res), inner))
        if res.__class__ is System:
            sols.extend(res)
        else:
            sols.append(res)
    return sols


class System(frozenset):
    """A system of equations"""

    def solve_for(self, vals: Sequence[Var], groebner=False) -> System:
        if vals.__class__ is Var:
            return System(_foreach_solve(self, vals))
        if groebner:
            eqns = set(compute_grobner(self, list(vals)))
            if not eqns:
                return System(eqns)
        else:
            eqns = set(self)
        vals = list(vals)
        sols = []
        # Solve for each variable separately
        for _ in range(len(vals)):
            # Branched solving: previous variable had multiple solutions
            if sols and sols[0].__class__ is tuple:
                _branched_solve(vals, sols)
                continue
            # Choose the easiest variable to isolate
            eqn, v = next_eqn(eqns, vals)
            _solve(eqns, eqn, v, sols)
            vals.remove(v)
        if isinstance(sols[0], tuple):
            sols = [i.factor() for i, _ in sols]
        else:
            sols = [i.factor() for i in sols]
        return System(sols)

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

    def is_close(self, threshold: float = 1e-7):
        return all(eqn.is_close(threshold) for eqn in self)

    @steps.tracked()
    def expand(self):
        res = System(i.expand() for i in self)
        [register(i) for i in res]
        return res

    @steps.tracked()
    def factor(self):
        res = System(i.factor() for i in self)
        [register(i) for i in res]
        return res

    @steps.tracked()
    def subs(self, mapping: dict[Node]):
        res = [i.subs(mapping) for i in self]
        [register(i) for i in res]
        if len(res) == 1:
            return res.pop()
        return System(res)

    def totex(self) -> str:
        return "\\\\".join(map(lambda x: x.totex(1), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    @steps.tracked()
    def normalize(self) -> System:
        return System(i.normalize() for i in self)


__all__ = ["System"]
