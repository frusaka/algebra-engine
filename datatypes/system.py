from __future__ import annotations
from typing import Sequence

from utils import difficulty_weight
from datatypes.eval_trace import *

from .collection import Collection
from .variable import Variable


class System(Collection):
    """A system of equations or inequalities"""

    def __getitem__(self, vals: Sequence[Variable]) -> System:
        """Solve for a system of (in)equalities"""
        from processing import subs

        # Assumeably from internal solving process
        if vals.__class__ is Variable:
            steps.register(ETBranchNode(self))
            return self
        seen = set()

        def solve(eqns, v):
            # Find an (in)equality with an independent target variable
            try:
                idx, org = next(
                    (idx, org)
                    for idx, org in enumerate(eqns)
                    if org not in seen and v in org
                )
            except StopIteration:
                raise ValueError(f"No independent variable containg {v}")
            eqn = org[v]
            if eqn.__class__ is not self.__class__ and eqn.left.value != v:
                raise ArithmeticError(f"Could not solve for {v}")
            eqns.pop(idx)
            if eqn.__class__ is System:
                seen.update(eqn)
                steps.register(ETSubNode(v, ETBranchNode(i.right for i in eqn)))
                eqns = [
                    System(
                        res | {j}
                        if (res := subs(System(eqns), {v: j.right})).__class__ is System
                        else {res, j}
                    )
                    for j in eqn
                ]
                if len(eqns) == 1:
                    return list(eqns[0])
                return eqns
            seen.add(eqn)
            # Need a check for infinite solutions
            if eqn.left.value != v:
                return System(eqns + [eqn])
            # Substitute in the rest of equations
            steps.register(ETSubNode(v, eqn.right))
            for i in range(len(eqns)):
                eqns[i] = subs(eqns[i], {v: eqn.right})
            # Put the newly solved equation at the end
            eqns.append(eqn)
            return eqns

        eqns = sorted(
            self,
            key=lambda eqn: difficulty_weight(eqn.normalize().left),
        )

        steps.register(ETNode(self))
        # Solve for each variable separately
        with steps.branching(len(vals)) as branches:
            for idx, v in zip(branches, vals):
                steps.register(ETTextNode(f"Solve for {v}:"))
                if eqns[0].__class__ is System:
                    with steps.branching(len(eqns)) as branches:
                        for idx in branches:
                            steps.register(ETTextNode(f"Branch {idx+1}:"))
                            steps.register(ETNode(eqns[idx]))
                            eqns[idx] = System(solve(list(eqns[idx]), v))
                            steps.register(ETBranchNode(eqns[idx]))
                    # Flatten when necessary (most cases)
                    if next(iter(next(iter(eqns)))).__class__ is System:
                        eqns = list(j for i in eqns for j in i)
                    steps.register(ETBranchNode(eqns))
                    continue
                eqns = solve(eqns, v)
                if eqns.__class__ is System:
                    break
                if eqns[0].__class__ is System:
                    steps.register(ETBranchNode(eqns))
                else:
                    steps.register(ETNode(System(eqns)))
        seen.clear()
        return System(eqns)

    def __bool__(self) -> bool:
        return all(self)

    def __str__(self) -> str:
        res = []
        for i in self:
            if i.__class__ is System:
                res.append(str(i).join("()"))
            else:
                res.append(str(i))
        return ", ".join(res)

    def __repr__(self) -> str:
        return str(self).join("{}")

    def totex(self, align: bool = True) -> str:
        return "&" * align + "\\\\".join(map(lambda x: x.totex(align), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self, weaken=True) -> System:
        return System(i.normalize(weaken) for i in self)

    @staticmethod
    def clear_cache():
        return
