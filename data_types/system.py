from __future__ import annotations

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
        vals = tuple(vals)
        print(vals, "→", end=" ")
        # Solve for each variable separately
        for v in vals:
            idx, org = next((idx, i) for idx, i in enumerate(eqns) if v in i)
            print(System.__str__(eqns))
            print(v, "→", org)
            eqn = solve(v, org)
            # Multiple solutions not yet supported
            if isinstance(eqn, System):
                raise NotImplementedError("Can't handle multiple solutions")
            # Substitute in the rest of equations
            old = v.join(("\033[31m", "\033[0m"))
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
        return System(eqns)

    def __bool__(self) -> bool:
        return all(self)

    def __add__(self, value: Term):
        return System(t + value for t in self)

    def __sub__(self, value: Term):
        return System(t - value for t in self)

    def __mul__(self, value: Term):
        return next(iter(v)) if len(v := System(t * value for t in self)) == 1 else v

    def __truediv__(self, value: Term):
        return System(t / value for t in self)

    def __pow__(self, value: Term):
        return next(iter(v)) if len(v := System(t**value for t in self)) == 1 else v

    def __str__(self) -> str:
        return "; ".join((str(i) for i in self))

    @property
    def value(self):
        return self
