from __future__ import annotations
from functools import lru_cache
from typing import Sequence

from utils import difficulty_weight, STEPS

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
            STEPS.append(self.totex())
            return self
        eqns = sorted(
            self,
            key=lambda eqn: difficulty_weight(eqn.normalize().left),
        )

        if vals.__class__ is str:
            vals = (Variable(vals),)
        # Solve for each variable separately
        for v in vals:
            STEPS.append(System.totex(eqns))
            if len(vals) > 1:
                STEPS.append("\\text{Solve for " + v + "}")
            if eqns[0].__class__ is System:

                for idx, eqn in enumerate(eqns):
                    j = len(STEPS)

                    eqns[idx] = eqn[str(v)]
                    STEPS[j:] = [
                        "\\\\".join("\\qquad " + i for i in STEPS[j:]),
                        "\\text{ }",
                    ]
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
                return System(eqns)
            eqn = org[v]
            eqns.pop(idx)
            old = "\\textcolor{#d7170b}" + v.join("{}")
            if eqn.__class__ is System:
                new = ",".join(
                    map(
                        lambda x: "\\textcolor{#21ba3a}" + x.right.totex().join("{}"),
                        eqn,
                    )
                ).join("{}")
                STEPS.append("\\text{Substitute }" + old + "\\text{ with }" + new)
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
                new = "\\textcolor{#21ba3a}" + eqn.right.totex().join("{}")
                STEPS.append("\\text{Substitute }" + old + "\\text{ with }" + new)
                for i in range(len(eqns)):
                    eqns[i] = subs(eqns[i], {v: eqn.right})
                # Put the newly solved equation at the end
                eqns.append(eqn)
        STEPS.append(System.totex(eqns))
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

    def totex(self) -> str:
        return "\\\\".join(map(lambda x: x.totex(), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self, weaken=True) -> System:
        return System(i.normalize(weaken) for i in self)
