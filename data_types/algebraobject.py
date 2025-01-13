from __future__ import annotations
from dataclasses import dataclass
import math
from .bases import Base
from .number import Number
from .variable import Variable
from .collection import Collection
from .product import Product
from .polynomial import Polynomial
from utils import Proxy, print_coef


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
                    print_coef(self.coef), AlgebraObject(value=self.value, exp=self.exp)
                )
            return (
                str(AlgebraObject(value="$", exp=self.exp))
                .join("()")
                .replace("$", str(self.value))
            )
        if self.exp_const() < 0:
            return "{0}/{1}".format(
                self.coef.numerator,
                AlgebraObject(Number(self.coef.denominator), self.value, -self.exp),
            )
        if "/" in str(self.coef):
            return "{0}/{1}".format(self.numerator, self.denominator)
        res = print_coef(self.coef)
        if isinstance(self.value, Collection) and isinstance(
            self.numerator.value, Number
        ):
            if not res or res == "-":
                res = str(self.coef)
            res += "/" + str(self.denominator.value)
        else:
            res += str(self.value)
        if self.exp == 1:
            return res
        exp = self.exp_const()
        if exp.denominator != 1:
            if self.coef != 1:
                val = AlgebraObject(value=self.value, exp=self.exp)
                if self.coef == -1:
                    return "-{0}".format(val)
                return "{0}({1})".format(print_coef(self.coef), val)
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
        a, b = AlgebraObject.rationalize(a, b)
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

    def gcd_coefs(self):
        coef = self.tovalue()
        was_imag = 0
        if coef.numerator.imag:
            yield int(coef.numerator.real)
            yield int(coef.numerator.imag)
            was_imag = 1
        if isinstance(self.value, Polynomial) and abs(self.exp) == 1:
            for i in self.value:
                yield from i.gcd_coefs()
            if self.exp == 1:
                return
        if not was_imag:
            yield coef.numerator

    @property
    def numerator(self):
        if isinstance(self.value, Product):
            return self.value.numerator * AlgebraObject(Number(self.coef.numerator))
        if self.exp_const() > 0:
            return AlgebraObject(Number(self.tovalue().numerator), self.value, self.exp)
        return AlgebraObject(Number(self.tovalue().numerator))

    @property
    def denominator(self):
        if isinstance(self.value, Product):
            return self.value.denominator * AlgebraObject(Number(self.coef.denominator))
        if self.exp_const() < 0:
            return (
                AlgebraObject(Number(self.coef.denominator), self.value, self.exp)
                ** -AlgebraObject()
            )
        return AlgebraObject(Number(self.tovalue().denominator))

    @property
    def remainder(self):
        if self.denominator.value != 1:
            return self.numerator
        if self.exp != 1:
            return AlgebraObject(Number(0))
        if isinstance(self.value, Polynomial):
            for i in self.value:
                if i.denominator.value == 1:
                    return i.numerator
        return AlgebraObject(Number(0))

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

    @staticmethod
    def rationalize(a: AlgebraObject, b: AlgebraObject):
        if a.denominator.value != 1:
            return a.rationalize(a * a.denominator, b * a.denominator)
        if b.denominator.value != 1:
            return a.rationalize(a * b.denominator, b * b.denominator)
        if a.exp == 1 and isinstance(a.value, Polynomial):
            for i in a.value:
                if i.denominator.value != 1:
                    return a.rationalize(a * i.denominator, b * i.denominator)
        if b.exp == 1 and isinstance(b.value, Polynomial):
            for i in b.value:
                if i.denominator.value != 1:
                    return a.rationalize(a * i.denominator, b * i.denominator)
        gcd = math.gcd(*a.gcd_coefs(), *b.gcd_coefs())
        if gcd != 1:
            gcd = AlgebraObject(Number(gcd) ** -1)
            a *= gcd
            b *= gcd
        return a, b

    @staticmethod
    def gcd(a: AlgebraObject, b: AlgebraObject):
        while b.value != 0:
            r = (a / b).remainder
            if r == a:
                return AlgebraObject()
            a, b = b, r
        return a

    @staticmethod
    def lcm(a: AlgebraObject, b: AlgebraObject):
        gcd = AlgebraObject.gcd(a, b)
        if gcd.value == 1:
            gcd = AlgebraObject.gcd(b, a)
        return (a * b) / gcd
