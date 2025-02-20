from __future__ import annotations

from utils import difficulty_weight

from .collection import Collection
from .variable import Variable
from .term import Term
from .number import Number

from typing import Sequence


def plus_minus_key(t: Term) -> Term:
    if not isinstance(t.value, Number) or not t.value.numerator.imag:
        return abs(t)
    return t


class System(Collection):
    """A system of equations or inequalities"""

    def __getitem__(self, vals: Sequence[Variable]) -> System:
        """Solve for a system of (in)equalities"""
        from processing import solve, subs

        # Assumeably from internal solving process
        if isinstance(vals, Variable):
            print(self)
            return self
        eqns = list(self)
        eqns = sorted(
            self,
            key=lambda eqn: difficulty_weight(eqn.left + eqn.right),
        )
        print(vals, "→", end=" ")
        if isinstance(vals, str):
            vals = (Variable(vals),)
        # Solve for each variable separately
        for v in vals:
            print(System.__str__(eqns))
            if isinstance(eqns, System):
                eqns = System(eqn[str(v)] for eqn in eqns)
                # Flatten when necessary (most cases)
                if isinstance(next(iter(next(iter(eqns)))), System):
                    eqns = System(j for i in eqns for j in i)
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
                    f"Could not find independent (in)equality containing '{v}'"
                )
            print(v, "→", org)
            eqn = solve(v, org, 0)
            old = v.join(("\033[31m", "\033[0m"))
            if isinstance(eqn, System):
                new = ", ".join(str(i.right).join(("\033[32m", "\033[0m")) for i in eqn)
                print(f"Substitute {old} with {new}")
                for i in range(len(eqns)):
                    if i == idx:
                        continue
                    eqns[i] = System(
                        System({j, subs(eqns[i], {v: j.right})}) for j in eqn
                    )
                eqns.pop(idx)
                if len(eqns) == 1:
                    eqns = eqns.pop()

            else:
                # Substitute in the rest of equations
                new = str(eqn.right).join(("\033[32m", "\033[0m"))
                print(f"Substitute {old} with {new}")
                for i in range(len(eqns)):
                    if i == idx:
                        continue
                    eqns[i] = subs(eqns[i], {v: eqn.right})
                # Put the newly solved equation at the end
                eqns.pop(idx)
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
            if isinstance(i, type(self)):
                res.append(str(i).join("()"))
            else:
                res.append(str(i))
        return "; ".join(res)
