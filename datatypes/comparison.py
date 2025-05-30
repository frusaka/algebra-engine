from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from enum import Enum

from .collection import Collection
from .system import System
from .polynomial import Polynomial
from .product import Product
from .number import Number, ZERO
from .variable import Variable
from .term import Term
from datatypes.eval_trace import *
from utils import quadratic, SYMBOLS, log_step


class CompRel(Enum):
    EQ = 0
    NE = 0.5
    LT = 1
    GT = 2
    LE = 3
    GE = 4

    def reverse(self):
        if self.value < 1:
            return self
        if self.name.startswith("L"):
            return getattr(CompRel, self.name.replace("L", "G"))
        return getattr(CompRel, self.name.replace("G", "L"))

    def __str__(self):
        return SYMBOLS.get(self.name)

    def totex(self):
        if self.name.endswith("E"):
            return "&" + f"\\{self.name.lower()}"
        return "&" + SYMBOLS.get(self.name)


@dataclass(frozen=True, slots=True)
class Comparison:
    left: Term
    right: Term
    rel: CompRel = CompRel.EQ

    def __str__(self) -> str:
        rel = self.rel
        if self.right.__class__ is Collection:
            rel = "∈"
        return "{0} {2} {1}".format(self.left, self.right, rel)

    @lru_cache
    def __getitem__(self, value: Variable) -> Comparison:
        """
        This method will be called when solving for a variable
        """
        # NOTE: if val>0:... checks are not necessary, they just make the solving process look natural
        log_step(ETNode(self))
        if value not in self:
            return self

        # Rewrite the comparison to put the target variable on the left
        if value in self.right and not value in self.left:
            self = self.reverse()
            log_step(ETNode(self))
        # Power lhs if it is a radical
        if value in self.left and (exp := self.left.exp.denominator) != 1:
            return (self ** Term(Number(exp)))[value]
        remove = []
        # Moving target terms to the left
        if self.right.value.__class__ is Polynomial:

            if value in self.right:
                if self.right.exp != 1:
                    if (exp := self.right.exp.denominator) != 1:
                        return (self ** Term(Number(exp)))[value]
                    return (self - self.right)[value]
                for t in self.right.value:
                    if value in t:
                        remove.append(t)
                if remove:
                    if len(remove) == 1:
                        remove = remove.pop()
                    else:
                        remove = Term(value=Polynomial(remove))
                    return (self - remove)[value]
        if value in self.right:
            return (self - self.right)[value]

        if self.left.coef != 1:
            return (self / Term(self.left.coef))[value]
        if self.left.exp != 1:
            exp = Term(value=self.left.exp).inv
            if value in exp:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self**exp)[value]

        if self.left.value.__class__ is Polynomial:
            for i in self.left.value:
                if not value in i:
                    remove.append(i)  # Not moving it yet, need to check for quadratics
                    continue
                # Term is in radical form
                if i.exp.denominator != 1:
                    self -= self.left - i
                    log_step(ETNode(self))
                    return (self.reverse() ** Term(Number(i.exp.denominator)))[value]

            # Solving using the quadratic formula
            # Moved to the right anyway to reduce redundancy
            if res := quadratic(self, value):
                pos, neg = res
                lhs = Term(value=value)
                if pos == neg and self.rel is CompRel.EQ:
                    res = Comparison(lhs, pos, self.rel)
                    log_step(ETNode(res))
                else:
                    res = System(
                        {
                            Comparison(lhs, pos, self.rel),
                            Comparison(lhs, neg, self.rel.reverse()),
                        }
                    )
                    log_step(ETBranchNode(res))
                return res
            if remove:
                if len(remove) == 1:
                    remove = remove.pop()
                else:
                    remove = Term(value=Polynomial(remove))
                return (self - remove)[value]
            # Brute-force factorization
            if (gcd := self.left.value.gcd()).value != 1:
                if value not in (t := self.left / gcd):
                    return (self / t)[value]
                elif value not in gcd:
                    return (self / gcd)[value]

        # Isolation by division
        if self.left.value.__class__ is Product:
            for t in self.left.value:
                exp = t.exp_const()
                if not value in t or exp < 0:
                    return (self / t)[value]

        return self

    def __contains__(self, value: Variable) -> bool:
        return value in self.left or value in self.right

    def __sub__(self, value: Term) -> Comparison:
        if value.to_const() > 0:
            log_step(ETOperatorNode(ETOperatorType.SUB, value))
        else:
            log_step(ETOperatorNode(ETOperatorType.ADD, -value))
        return Comparison(self.left + -value, self.right + -value, self.rel)

    def __truediv__(self, value: Term) -> Comparison:
        if value.denominator.value == 1:
            log_step(ETOperatorNode(ETOperatorType.DIV, value))
        else:
            log_step(ETOperatorNode(ETOperatorType.TIMES, value.inv))
        return Comparison(
            self.left / value,
            self.right / value,
            self.reverse_sign(value),
        )

    def __pow__(self, value: Term) -> Comparison:
        if value.denominator.value != 1 and value.numerator.value == 1:
            log_step(ETOperatorNode(ETOperatorType.SQRT, value.inv))
        else:
            log_step(ETOperatorNode(ETOperatorType.POW, value))
        lhs = self.left**value
        rhs = self.right**value
        # plus/minus trick for even roots
        if (
            (rhs.value != 0 or self.rel is not CompRel.EQ)
            and value.exp == 1
            and value.value.__class__ is Number
            and not value.value.denominator % 2
        ):
            return System(
                {
                    Comparison(lhs, rhs, self.rel),
                    Comparison(lhs, -rhs, self.rel.reverse()),
                }
            )
        return Comparison(lhs, rhs, self.rel)

    def __bool__(self) -> bool:
        return getattr(self.left, self.rel.name.lower().join(("__", "__")))(self.right)

    def reverse(self) -> Comparison:
        """Write the comparison in reverse"""
        return Comparison(self.right, self.left, self.rel.reverse())

    def normalize(self, weaken=True) -> Comparison:
        """Put all terms on the lhs"""
        return Comparison(
            self.left - self.right,
            Term(ZERO),
            CompRel.EQ if weaken else self.rel,
        )

    def reverse_sign(self, value: Term) -> CompRel:
        if self.rel is CompRel.EQ:
            return self.rel
        # Cannot assume the sign of the value is always positive
        if value.value.__class__ is not Number:
            raise ValueError(f"unknown sign of {value}")
        if value.value < 0:
            return self.rel.reverse()
        return self.rel

    def totex(self) -> str:
        left, rel, right = self.left, self.rel, self.right
        if self.right.__class__ is Collection:
            rel = "\\in"
        else:
            rel = rel.totex()
        if left.__class__ is tuple:
            left = ",".join(left).join(("\\left(", "\\right)"))
        else:
            left = left.totex()
        if right.__class__ is tuple:
            right = ",".join(map(lambda x: x.totex(), right)).join(
                ("\\left(", "\\right)")
            )
        else:
            right = right.totex()
        return "{0}{2}{1}".format(left, right, rel)
