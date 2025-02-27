from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from utils.constants import SYMBOLS
from .system import System
from .polynomial import Polynomial
from .product import Product
from .number import Number
from .variable import Variable
from .term import Term
from utils import quadratic, quadratic_formula


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


@dataclass(frozen=True, slots=True)
class Comparison:
    left: Term
    right: Term
    rel: CompRel = CompRel.EQ

    def __str__(self) -> str:
        return "{0} {2} {1}".format(self.left, self.right, self.rel).replace(
            "typing.", ""
        )

    def __getitem__(self, value: Variable) -> Comparison:
        """
        This method will be called when solving for a variable
        """
        # NOTE: if val>0:... checks are not necessary, they just make the solving process look natural
        print(self)
        if not (value in self.left or value in self.right):
            return self

        # Rewrite the comparison to put the target variable on the left
        if value in self.right and not value in self.left:
            self = self.reverse()
            print(self)

        # Moving target terms to the left
        if isinstance(self.right.value, Polynomial):
            if value in self.right:
                if self.right.exp != 1:
                    return self.reverse_sub(self.right)[value]
                for t in self.right.value:
                    if value in t:
                        return self.reverse_sub(t)[value]
        if value in self.right:
            return self.reverse_sub(self.right)[value]

        if self.left.coef != 1:
            return self.reverse_div(Term(self.left.coef))[value]
        if self.left.exp != 1:
            exp = Term(value=self.left.exp).inv
            if value in exp:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self**exp)[value]

        if isinstance(self.left.value, Polynomial):
            # Brute-force factorization
            t = self.left / Term(value=value, exp=self.left.get_exp(value))
            if not value in t:
                return self.reverse_div(t)[value]
            remove = None
            for i in self.left.value:
                if not value in i:
                    remove = i  # Not moving it yet, need to check for quadratics
                    continue
                # Term is in a fraction
                if isinstance(i.value, Product):
                    for t in i.value:
                        if t.exp_const() < 0:
                            return (self * t.inv)[value]
                elif (exp := i.exp_const()) < 0:
                    return (self * Term(value=i.value, exp=i.exp).inv)[value]
                # Term is in radical form
                elif exp.denominator != 1:
                    self = self.reverse_sub(self.left - i)
                    print(self)
                    return (
                        Comparison(self.right, self.left, self.rel.reverse())
                        ** Term(Number(exp.denominator))
                    )[value]

            # Solving using the quadratic formuala
            if (res := quadratic(self, value)) is not None:
                pos, neg = quadratic_formula(*res)
                lhs = Term(value=value)
                if pos == neg and self.rel is CompRel.EQ:
                    res = Comparison(lhs, pos, self.rel)
                else:
                    res = System(
                        {
                            Comparison(lhs, pos, self.rel),
                            Comparison(lhs, neg, self.rel.reverse()),
                        }
                    )
                print(res)
                return res

            if remove:
                return self.reverse_sub(remove)[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                exp = t.exp_const()
                if not value in t or exp < 0:
                    return self.reverse_div(t)[value]

        return self

    def __contains__(self, value: Variable) -> bool:
        return value in self.left or value in self.right

    def __add__(self, value: Term) -> Comparison:
        self.show_operation("+", value)
        return Comparison(self.left + value, self.right + value, self.rel)

    def __sub__(self, value: Term) -> Comparison:
        self.show_operation("-", value)
        return Comparison(self.left - value, self.right - value, self.rel)

    def __mul__(self, value: Term) -> Comparison:
        self.show_operation("*", value)
        # Reverse the signs when multiplying by a negative number
        return Comparison(
            self.left * value,
            self.right * value,
            self.rel if value.to_const() >= 0 else self.rel.reverse(),
        )

    def __truediv__(self, value: Term) -> Comparison:
        self.show_operation("/", value)
        return Comparison(
            self.left / value,
            self.right / value,
            self.rel if value.to_const() > 0 else self.rel.reverse(),
        )

    def __pow__(self, value: Term) -> Comparison:
        self.show_operation("^", value)
        lhs = self.left**value
        rhs = self.right**value
        # plus/minus trick for even roots
        if (
            rhs.value != 0
            and value.exp == 1
            and isinstance(value.value, Number)
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

    def reverse_sub(self, value: Term) -> Comparison:
        """Intuitively Log inverse subtration"""
        if value.to_const() > 0:
            return self - value
        return self + -value

    def reverse_div(self, value: Term) -> Comparison:
        """Intuitively Log inverse division"""
        if value.denominator.value != 1:
            return self * value.inv
        return self / value

    def show_operation(self, operator: str, value: Term) -> None:
        """A convinent method to show the user the solving process"""
        print(" " * str(self).index(str(self.rel)), operator + " ", value, sep="")
