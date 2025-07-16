from __future__ import annotations
import itertools
import math
from typing import Iterable, Sequence, TYPE_CHECKING


from datatypes.base import Node


from .eval_trace import *

from datatypes import *
from .utils import arrange_eqns, compute_grobner, next_eqn
from utils.print_ import print_system
import utils


def _solve(eqns: set, org, v, sols):
    eqn = org.solve_for(v)
    eqns.remove(org)
    if eqn.__class__ is System:
        ETSteps.register(ETSubNode(v, ETBranchNode(i.right for i in eqn)))
        new_eqns = []
        for i in eqn:
            if i.left != v:
                continue
            new_eqns.append(
                (
                    System([j.subs({v: i.right}) for j in sols] + [i]),
                    {j.subs({v: i.right}) for j in eqns},
                )
            )
        if len(new_eqns) == 1:
            new_eqns = list(new_eqns[0])
        sols[:] = new_eqns
        return
    # Need a check for infinite solutions
    if eqn.left != v:
        raise ArithmeticError(f"Could not solve for {v}")
    # Substitute in the rest of equations
    ETSteps.register(ETSubNode(v, eqn.right))
    for i in range(len(sols)):
        sols[i] = sols[i].subs({v: eqn.right})
    for j in eqns.copy():
        eqns.remove(j)
        eqns.add(j.subs({v: eqn.right}))

    # # Put the newly solved equation at the end
    sols.append(eqn)


def _branched_solve(vals, sols):
    _, v = next_eqn(sols[0][1], vals)
    ETSteps.register(ETTextNode(f"Solve for {v}"))

    with ETSteps.branching(len(sols)) as branches:
        for idx in branches:
            data, eqns = sols[idx]
            data = list(data)
            eqn, _ = next_eqn(eqns, [v])
            if eqn.left == v:
                data.append(eqn)
                eqns.remove(eqn)
                sols[idx] = System(data), eqns
                continue
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            # ETSteps.register(ETNode(System({*sols[idx][0], *sols[idx][1]})))
            _solve(eqns, eqn, v, data)
            if data[0].__class__ is tuple:
                ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in data))
                sols.extend(data)
                sols[idx] = None
            else:
                sols[idx] = System(data), eqns
                ETSteps.register(ETNode(System({*data, *eqns})))
    # Flattening in case of double multiple solutions
    while True:
        for idx in range(len(sols)):
            if sols[idx] is None:
                sols.pop(idx)
                break
        else:
            break
    ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in sols))
    vals.remove(v)


def _foreach_solve(eqns, value):
    ETSteps.register(ETBranchNode(eqns))
    if not any(eqn.left != value for eqn in eqns):
        return eqns
    # Branched during the solving process
    sols = []
    with ETSteps.branching(len(eqns)) as branches:
        for idx, eqn in zip(branches, eqns):
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            try:
                res = eqn.solve_for(value)
            except ArithmeticError as err:
                ETSteps.register(ETTextNode(repr(err), "#d7170b"))
                continue
            if res.__class__ is System:
                sols.extend(res)
            else:
                sols.append(res)
    return sols


class System(frozenset):
    """A system of equations"""

    def solve_for(self, vals: Sequence[Var], groebner=True) -> System:
        if vals.__class__ is Var:
            return System(_foreach_solve(self, vals))

        ETSteps.register(ETTextNode("Solving for " + str(vals)[1:-1]))
        ETSteps.register(ETNode(self))
        if groebner:
            eqns = compute_grobner(self, list(vals))
            if not eqns:
                return System(eqns)
            if eqns != self:
                ETSteps.register(ETNode(System(eqns)))
        else:
            eqns = set(self)
        vals = set(vals)
        sols = []
        # Solve for each variable separately
        with ETSteps.branching(len(vals)) as branches:
            for _ in branches:
                # Branched solving: previous variable had multiple solutions
                if sols and sols[0].__class__ is tuple:
                    _branched_solve(vals, sols)
                    continue
                # Choose the easiest variable to isolate
                eqn, v = next_eqn(eqns, vals)
                ETSteps.register(ETTextNode(f"Solve for {v}"))
                _solve(eqns, eqn, v, sols)
                if sols[0].__class__ is tuple:
                    ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in sols))
                else:
                    ETSteps.register(ETNode(System({*sols, *eqns})))
                vals.remove(v)
        if isinstance(sols[0], tuple):
            sols = [i.simplify() for i, _ in sols]
        else:
            sols = [i.simplify() for i in sols]
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

    def expand(self):
        return System(i.expand() for i in self)

    def simplify(self):
        return System(i.simplify() for i in self)

    def subs(self, mapping: dict[Var, Node]) -> System:
        return System(i.subs(mapping) for i in self)

    def totex(self) -> str:
        return "\\\\".join(map(lambda x: x.totex(1), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self) -> System:
        return System(i.normalize() for i in self)


__all__ = ["System"]
