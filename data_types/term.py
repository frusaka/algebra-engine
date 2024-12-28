from dataclasses import dataclass
from .bases import *
from .product import Product
from .polynomial import Polynomial
from utils import clean


@dataclass(order=True, frozen=True)
class Term:
    coef: Number = Number(1)
    value: Base = Number(1)
    exp: Base = Number(1)

    def __hash__(self):
        return hash((self.__class__, self.coef, self.value, self.exp))

    def __str__(self):
        res = ""
        exp = str(self.exp)
        if not isinstance(self.value, Number):
            if abs(self.coef) != 1:
                res = str(self.coef)
                if "/" in res:
                    res = res.join("()")
            elif self.coef == -1:
                res = "-"
        else:
            res = str(self.value)
            if "/" in res and self.exp != 1:
                res = res.join("()")
        if not isinstance(self.value, Number):
            res += str(self.value)

        if isinstance(self.exp, Number):
            if self.exp == 1:
                return res
            if self.exp < 0:
                # TODO: Add similar support for negative Term exponents
                return "{0}/{1}".format(
                    self.coef.numerator,
                    Term(Number(self.coef.denominator), self.value, abs(self.exp)),
                )
            if self.exp.denominator != 1:
                if self.coef != 1:
                    return "{0}({1})".format(
                        "-" if self.coef == -1 else self.coef,
                        Term(value=self.value, exp=self.exp),
                    )
                if self.exp.numerator != 1:
                    res = "{0}^{1}".format(res, self.exp.numerator)
                return "{0}√{1}".format(self.exp.denominator, res)
        elif self.exp.coef != 1:
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

    @clean
    def __add__(a, b):
        return a.value.add(Proxy(b), a) or Term(value=Polynomial([a, b]))

    @clean
    def __sub__(a, b):
        return a + -b

    @clean
    def __mul__(a, b):
        return a.value.mul(Proxy(b), a) or Product.mul(
            Proxy(b), Term(a.coef, Product([Term(value=a.value, exp=a.exp)]))
        )

    @clean
    def __truediv__(a, b):
        if isinstance(a.value, Polynomial) and isinstance(b.value, Polynomial):
            return Polynomial.long_division(a, b)
        return a * b ** -Term()

    @clean
    def __pow__(a, b):
        if a.value == 1:
            return a
        if b.value == 0:
            return Term()
        if not isinstance(a.value, Product) and (
            isinstance(a.exp, Term) or (not isinstance(b.value, Number) or b.exp != 1)
        ):
            res = Term(a.coef, a.value) ** b.tovalue()
            c = Term(res.coef, res.value, Term(value=a.exp) * (b / b.tovalue()))
            if abs(b.tovalue().value) != 1:
                print(
                    f"WARNING: {a}^{b} = {c} only if {(b / b.tovalue())} is a real integer"
                )
            return Term(res.coef, res.value, Term(value=a.exp) * (b / b.tovalue()))
        return a.value.pow(Proxy(b), a)

    def __pos__(self):
        return self

    def __neg__(self):
        return self * Term(value=Number(-1))

    def __abs__(self):
        if not isinstance(self.value, Number):
            return Term(abs(self.coef), self.value, self.exp)
        return Term(value=abs(self.value), exp=self.exp)

    def tovalue(self):
        if isinstance(self.value, Number):
            return Term(value=self.value)
        return Term(value=self.coef)

    def like(self, other, exp=1):

        if (
            not isinstance(other, Term)
            or not self.exp.like(other.exp)
            or not isinstance(other.value, type(self.value))
            or (exp)
            and (
                self.exp != other.exp
                or isinstance(other.value, Number)
                and (self.exp != 1 or other.exp != 1)
            )
        ):
            return 0
        if not isinstance(other.value, Number):
            return self.value == other.value
        return 1
