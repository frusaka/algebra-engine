from __future__ import annotations
from dataclasses import dataclass
from .bases import Base
from .number import Number
from .variable import Variable
from .collection import Collection
from .product import Product
from .polynomial import Polynomial
from utils import Proxy


@dataclass(order=True)
class AlgebraObject:
    coef: Number
    value: Base[Number, Variable, Product, Polynomial]
    exp: Number | AlgebraObject

    def __init__(self, coef=Number(1), value=Number(1), exp=Number(1)) -> None:
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

    def __hash__(self) -> int:
        return hash((self.__class__, self.coef, self.value, self.exp))

    def __str__(self) -> str:
        if isinstance(self.value, Number) and self.exp != 1:
            if self.coef != 1:
                return "{0}{1}".format(
                    self.coef, AlgebraObject(value=self.value, exp=self.exp)
                )
            return (
                str(AlgebraObject(value="$", exp=self.exp))
                .join("()")
                .replace("$", str(self.value))
            )
        if "/" in str(self.coef):
            return "{0}/{1}".format(self.numerator, self.denominator)
        res = ""
        if self.coef != 1:
            res = str(self.coef)
            if not self.coef.numerator.real:
                res = res.join("()")
        if self.coef == -1:
            res = "-"
        if isinstance(self.value, Collection) and isinstance(
            self.numerator.value, Number
        ):
            if not res or res == "-":
                res = str(self.coef)
            res += "/" + str(self.denominator.value)
        else:
            res += str(self.value)
        exp = self.exp if isinstance(self.exp, Number) else self.exp.coef
        if self.exp == 1:
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

    def __contains__(self, value: Variable) -> bool:
        if isinstance(self.value, Collection):
            return any(value in t for t in self.value)
        if (
            self.value == value
            or isinstance(self.exp, AlgebraObject)
            and value in self.exp
        ):
            return True
        return False

    def __add__(a, b: AlgebraObject) -> AlgebraObject:
        if a.like(b):
            return a.value.add(Proxy(b), a)
        return Polynomial.resolve(Proxy(b), a)

    def __sub__(a, b: AlgebraObject) -> AlgebraObject:
        return a + -b

    def __mul__(a, b: AlgebraObject) -> AlgebraObject:
        if v := a.split_const_from_exp():
            return b * v * AlgebraObject(a.coef, a.value, a.exp - AlgebraObject())
        if v := b.split_const_from_exp():
            return a * v * AlgebraObject(b.coef, b.value, b.exp - AlgebraObject())
        return a.value.mul(Proxy(b), a) or Product.resolve(a, b)

    def __truediv__(a, b: AlgebraObject) -> AlgebraObject:
        if isinstance(a.value, Polynomial) and not isinstance(b.value, Number):
            return Polynomial.long_division(a, b)
        return a * b ** -AlgebraObject()

    def __pow__(a, b: AlgebraObject) -> AlgebraObject:
        if b.value == 0:
            return AlgebraObject()
        return a.value.pow(Proxy(b), a) or (
            AlgebraObject(a.coef) ** b
            * AlgebraObject(value=a.value, exp=AlgebraObject(value=a.exp) * b)
        )

    def __pos__(self) -> AlgebraObject:
        return self

    def __neg__(self) -> AlgebraObject:
        return self * AlgebraObject(value=Number(-1))

    def __abs__(self) -> AlgebraObject:
        if not isinstance(self.value, Number) or self.exp != 1:
            return AlgebraObject(abs(self.coef), self.value, self.exp)
        return AlgebraObject(value=abs(self.value), exp=self.exp)

    @property
    def numerator(self):
        if isinstance(self.value, Product):
            return self.value.numerator * AlgebraObject(Number(self.coef.numerator))
        if self.exp_const() > 0:
            return AlgebraObject(Number(self.coef.numerator), self.value, self.exp)
        return AlgebraObject(Number(self.coef.numerator))

    @property
    def denominator(self):
        if isinstance(self.value, Product):
            return self.value.denominator * AlgebraObject(Number(self.coef.denominator))
        if self.exp_const() < 0:
            return AlgebraObject(Number(self.coef.denominator), self.value, -self.exp)
        return AlgebraObject(Number(self.coef.denominator))

    def exp_const(self) -> Number:
        return self.exp if isinstance(self.exp, Number) else self.exp.coef

    def tovalue(self) -> Number:
        if isinstance(self.value, Number) and self.exp == 1:
            return self.value
        return self.coef

    def split_const_from_exp(self) -> AlgebraObject | None:
        if isinstance(self.exp, Number):
            return
        if isinstance(self.exp.value, Polynomial) and self.exp.exp == 1:
            for i in self.exp.value:
                if i.value == 1:
                    return AlgebraObject(value=self.value)

    def like(self, other, exp=1) -> bool:
        if not isinstance(other, AlgebraObject):
            return False
        # Assumes in the case of multiplications, values with the same base are like terms
        if not exp and self.value == other.value:
            return True

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
            return False
        if not isinstance(other.value, Number):
            return self.value == other.value
        return True
