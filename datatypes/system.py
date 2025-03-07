from __future__ import annotations
from functools import lru_cache
from typing import Sequence

from utils import difficulty_weight

from .collection import Collection
from .variable import Variable
from .term import Term
from .number import Number


def plus_minus_key(t: Term) -> Term:
    if not t.value.__class__ is Number or not t.value.numerator.imag:
        return abs(t)
    return t


class System(Collection):
    """A system of equations or inequalities"""

    @lru_cache
    def __getitem__(self, vals: Sequence[Variable]) -> System:
        """Solve for a system of (in)equalities"""
        from processing import subs

        # Assumeably from internal solving process
        if vals.__class__ is Variable:
            print(self)
            return self
        eqns = sorted(
            self,
            key=lambda eqn: difficulty_weight(eqn.normalize().left),
        )

        if vals.__class__ is str:
            vals = (Variable(vals),)
        # Solve for each variable separately
        for v in vals:
            print(System.__str__(eqns))
            if eqns[0].__class__ is System:
                eqns = list(
                    (
                        print(
                            f"(Start Branch)\n".join(("\033[30m", "\033[0m")),
                            f"{v} →",
                            end=" ",
                            sep="",
                        ),
                        eqn[str(v)],
                        print("(End Branch)".join(("\033[30m", "\033[0m"))),
                    )[1]
                    for eqn in eqns
                )
                # Flatten when necessary (most cases)
                if next(iter(next(iter(eqns)))).__class__ is System:
                    eqns = list(j for i in eqns for j in i)
                continue
            # Find an (in)equality with an independent target variable
            for idx, org in enumerate(eqns):
                if any(
                    v in j and j.exp.denominator == 1 or j.value == v
                    for j in (org.left, org.right)
                ):
                    break
            else:
                raise ValueError(
                    f"Could not find independent equation containing '{v}'"
                )
            if len(vals) - 1:
                print(v, "→", org)
            eqn = org[v]
            eqns.pop(idx)
            old = v.join(("\033[31m", "\033[0m"))
            if eqn.__class__ is System:
                new = ", ".join(str(i.right).join(("\033[32m", "\033[0m")) for i in eqn)
                print(f"Substitute {old} with {new}")
                eqns = [
                    System(
                        res | {j}
                        if (res := subs(System(eqns), {v: j.right})).__class__ is System
                        else {res, j}
                    )
                    for j in eqn
                ]
                if len(eqns) == 1:
                    eqns = list(eqns[0])
            else:
                # Need a check for infinite solutions
                if eqn.left.value != v:
                    return System(eqns + [eqn])
                # Substitute in the rest of equations
                new = str(eqn.right).join(("\033[32m", "\033[0m"))
                print(f"Substitute {old} with {new}")
                for i in range(len(eqns)):
                    eqns[i] = subs(eqns[i], {v: eqn.right})
                # Put the newly solved equation at the end
                eqns.append(eqn)
        print(System.__str__(eqns))
        if len(eqns) == 1:
            return eqns.pop()
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
        return "; ".join(res)

    def normalize(self, weaken=True) -> System:
        return System(i.normalize(weaken) for i in self)
