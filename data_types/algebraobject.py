from __future__ import annotations
from dataclasses import dataclass
from .number import Number
from .variable import Variable
from .product import Product
from .polynomial import Polynomial
from utils import Proxy


@dataclass(order=True)
class AlgebraObject:
    coef: Number
    value: Number | Variable | Polynomial | Product
    exp: Number | AlgebraObject

    def __init__(self, coef=Number(1), value=Number(1), exp=Number(1)):
        if isinstance(value, AlgebraObject):
            self.coef, self.value, self.exp = value.coef, value.value, value.exp
            return
        # Cases when operations with exponents simplify to a constant
        if (
            isinstance(exp, AlgebraObject)
            and isinstance(exp.value, Number)
            and exp.exp == 1
        ):
            exp = exp.value
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
            return "{0}({1})".format(
                self.coef, AlgebraObject(value=self.value, exp=self.exp)
            )
        res = ""
        if self.coef != 1:
            res = str(self.coef)
            if self.coef.imag:
                res = res.join("()")
        if self.coef == -1:
            res = "-"
        res += str(self.value)
        exp = self.exp if isinstance(self.exp, Number) else self.exp.coef
        if exp == 1 and isinstance(self.exp, Number):
            return res
        if exp < 0:
            return "{0}/{1}".format(
                self.coef.numerator,
                AlgebraObject(Number(self.coef.denominator), self.value, -self.exp),
            )
        if exp.denominator != 1:
            if self.coef != 1:
                return "{0}({1})".format(
                    "-" if self.coef == -1 else self.coef,
                    AlgebraObject(value=self.value, exp=self.exp),
                )
            if exp.numerator != 1:
                res = "{0}^{1}".format(res, exp.numerator)
            return "{0}√{1}".format(exp.denominator, res)
        exp = str(self.exp)
        if isinstance(self.exp, AlgebraObject) and (
            self.exp.coef != 1 or self.exp.exp != 1
        ):
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

    def __add__(a, b):
        if a.like(b):
            return a.value.add(Proxy(b), a)
        return Polynomial.resolve(Proxy(b), a)

    def __sub__(a, b):
        return a + -b

    def __mul__(a, b):
        if v := a.split_const_from_exp():
            return b * v * (AlgebraObject(a.coef, a.value, a.exp - AlgebraObject()))
        return a.value.mul(Proxy(b), a) or Product.resolve(a, b)

    def __truediv__(a, b):
        if isinstance(a.value, Polynomial) and isinstance(b.value, Polynomial):
            return Polynomial.long_division(a, b)
        return a * b ** -AlgebraObject()

    def __pow__(a, b):
        if b.value == 0:
            return AlgebraObject()
        return a.value.pow(Proxy(b), a) or AlgebraObject(
            a.coef, a.value, type(a)(value=a.exp) * b
        )

    def __pos__(self):
        return self

    def __neg__(self):
        return self * AlgebraObject(value=Number(-1))

    def __abs__(self):
        if not isinstance(self.value, Number):
            return AlgebraObject(abs(self.coef), self.value, self.exp)
        return AlgebraObject(value=abs(self.value), exp=self.exp)

    def tovalue(self):
        if isinstance(self.value, Number) and self.exp == 1:
            return AlgebraObject(value=self.value)
        return AlgebraObject(value=self.coef)

    def split_const_from_exp(self):
        if isinstance(self.exp, Number):
            return
        if isinstance(self.exp.value, Polynomial) and self.exp.exp == 1:
            for i in self.exp.value:
                if i.value == 1:
                    return AlgebraObject(self.coef, self.value)

    def like(self, other, exp=1):
        if not isinstance(other, AlgebraObject):
            return 0
        # Assumes in the case of multiplications, values with the same base are like terms
        if not exp and self.value == other.value:
            return 1

        if (
            not self.exp.like(other.exp)
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
