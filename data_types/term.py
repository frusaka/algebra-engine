from dataclasses import dataclass
from .bases import *
from .product import Product
from .polynomial import Polynomial


@dataclass(order=True)
class Term:
    coef: Number
    value: Base
    exp: Base

    def __init__(self, coef=Number(1), value=Number(1), exp=Number(1)):
        if coef == 0:
            value = Number(0)
            coef = exp = Number(1)
        elif coef != 1 and value == 1:
            value, coef = coef, value
            exp = coef
        elif exp == 0:
            value = coef
            exp = coef = Number(1)
        # 1^n = 1 for any value of n
        elif value == 1:
            exp = value
        self.coef, self.value, self.exp = coef, value, exp

    def __hash__(self):
        return hash((self.__class__, self.coef, self.value, self.exp))

    def __str__(self):
        if self.coef != 1 and isinstance(self.value, Number):
            return str(self.coef) + f"({self.value}^{self.exp})"
        res = ""
        if abs(self.coef) != 1:
            res = str(self.coef)
            if "/" in res:
                res = res.join("()")
        elif self.coef == -1:
            res = "-"
        res += str(self.value)
        exp = self.exp if isinstance(self.exp, Number) else self.exp.coef
        if exp == 1 and isinstance(self.exp, Number):
            return res
        if exp < 0:
            return "{0}/{1}".format(
                self.coef.numerator,
                Term(Number(self.coef.denominator), self.value, -self.exp),
            )
        if exp.denominator != 1:
            if self.coef != 1:
                return "{0}({1})".format(
                    "-" if self.coef == -1 else self.coef,
                    Term(value=self.value, exp=self.exp),
                )
            if exp.numerator != 1:
                res = "{0}^{1}".format(res, exp.numerator)
            return "{0}√{1}".format(exp.denominator, res)
        exp = str(self.exp)
        if isinstance(self.exp, Term) and (self.exp.coef != 1 or self.exp.exp != 1):
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

    def __add__(a, b):
        if a.like(b):
            return a.value.add(Proxy(b), a)
        return Term(value=Polynomial([a, b]))

    def __sub__(a, b):
        return a + -b

    def __mul__(a, b):
        if v := a.value.mul(Proxy(b), a):
            return v
        # Like Bases
        if a.value == b.value:
            exp_a = a.exp if isinstance(a.exp, Term) else Term(value=a.exp)
            exp_b = b.exp if isinstance(b.exp, Term) else Term(value=b.exp)
            return Term(a.coef * b.coef, a.value, exp_a + exp_b)

        return Product.resolve(a, b)

    def __truediv__(a, b):
        if isinstance(a.value, Polynomial) and isinstance(b.value, Polynomial):
            return Polynomial.long_division(a, b)
        return a * b ** -Term()

    def __pow__(a, b):
        if a.value == 1:
            return a
        if b.value == 0:
            return Term()
        a_exp = a.exp if isinstance(a.exp, Term) else Term(value=a.exp)
        if isinstance(a.value, Number) and (
            not isinstance(b.value, Number) or b.exp != 1
        ):
            # NOTE: a^(nm) = (a^n)^m only if m is a real integer
            res = Term(a.coef, a.value) ** b.tovalue()
            return Term(res.coef, res.value, a_exp * (b / b.tovalue()))
        if v := a.value.pow(Proxy(b), a):
            return v
        if isinstance(a.exp, Term):
            return Term(a.coef, a.value, a.exp * b)
        return Term(a.coef, a.value, a_exp * b)

    def __pos__(self):
        return self

    def __neg__(self):
        return self * Term(value=Number(-1))

    def __abs__(self):
        if not isinstance(self.value, Number):
            return Term(abs(self.coef), self.value, self.exp)
        return Term(value=abs(self.value), exp=self.exp)

    def tovalue(self):
        if isinstance(self.value, Number) and self.exp == 1:
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
                and (self.exp != 1 and self.value != other.value)
            )
        ):
            return 0
        if not isinstance(other.value, Number):
            return self.value == other.value
        return 1
