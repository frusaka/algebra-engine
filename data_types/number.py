from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Any, SupportsFloat, SupportsComplex
from .bases import Base, Fraction
from utils import *


@dataclass(frozen=True, init=False)
class Number(Base):
    numerator: SupportsFloat | SupportsComplex | str
    denominator: SupportsFloat

    def __new__(
        cls,
        numerator: SupportsFloat | SupportsComplex | str = 0,
        denominator: SupportsFloat = 1,
    ) -> Number:
        obj = super().__new__(cls)
        if isinstance(numerator, complex) and numerator.imag:
            real = Fraction(Fraction(numerator.real), Fraction(denominator))
            imag = Fraction(Fraction(numerator.imag), Fraction(denominator))
            den = math.lcm(real.denominator, imag.denominator)
            object.__setattr__(
                obj,
                "numerator",
                complex(
                    (den / real.denominator) * real.numerator,
                    (den / imag.denominator) * imag.numerator,
                ),
            )
            object.__setattr__(obj, "denominator", den)
            return obj
        if isinstance(numerator, complex):
            numerator = numerator.real
        val = Fraction(Fraction(numerator), Fraction(denominator))
        object.__setattr__(obj, "numerator", val.numerator)
        object.__setattr__(obj, "denominator", val.denominator)
        return obj

    def __bool__(self) -> bool:
        return bool(self.numerator)

    def __str__(self):
        # Lazy print
        return (
            print_frac(self).replace("j", "i").replace("1i", "i").replace("1i", "11i")
        )

    def __repr__(self) -> str:
        return "Number(numerator={0}, denominator={1})".format(
            repr(self.numerator), repr(self.denominator)
        )

    def __add__(self, other: Number | SupportsFloat | SupportsComplex) -> Number:
        if not isinstance(other, Number):
            return self + Number(other)
        den = math.lcm(self.denominator, other.denominator)
        num_a = (den / self.denominator) * self.numerator
        num_b = (den / other.denominator) * other.numerator
        return Number(num_a + num_b, den)

    def __sub__(self, other: Number | SupportsFloat | SupportsComplex) -> Number:
        return self + -other

    def __mul__(self, other: Number | SupportsFloat | SupportsComplex) -> Number:
        if not isinstance(other, Number):
            return self * Number(other)
        return Number(
            self.numerator * other.numerator, self.denominator * other.denominator
        )

    def __truediv__(self, other: Number | SupportsFloat | SupportsComplex) -> Number:
        if not isinstance(other, Number):
            return self / Number(other)
        num = self.numerator * other.denominator
        den = self.denominator * other.numerator
        if den.imag:
            conjugate = complex(den.real, -den.imag)
            num *= conjugate
            den *= conjugate
            return Number(num, den.real)
        return Number(num, den)

    def __pow__(self, other: Number | SupportsFloat | SupportsComplex) -> Number:
        if not isinstance(other, Number):
            return self ** Number(other)
        if other.numerator < 0:
            return Number(1) / (self**-other)
        num = self.nth_root(self.numerator**other.numerator, other.denominator)
        den = self.nth_root(self.denominator**other.numerator, other.denominator)
        return Number(num) / Number(den)

    def __abs__(self) -> Number:
        return Number(abs(self.numerator), self.denominator)

    def __neg__(self) -> Number:
        return Number(-self.numerator, self.denominator)

    def __pos__(self) -> Number:
        return self

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, (float, int, complex, Fraction, Number)):
            return False
        if not isinstance(value, Number):
            return self == Number(value)
        return (
            self.numerator == value.numerator and self.denominator == value.denominator
        )

    def __ne__(self, value: Any) -> bool:
        return not self == value

    def __gt__(self, value: Number | SupportsFloat | SupportsComplex) -> bool:
        if not isinstance(value, Number):
            return self > Number(value)
        if self.numerator.imag or value.numerator.imag:
            return False
        return Fraction(self.numerator, self.denominator) > Fraction(
            value.numerator, value.denominator
        )

    def __ge__(self, value: Number | SupportsFloat | SupportsComplex) -> bool:
        return self > value or self == value

    def __lt__(self, value: Number | SupportsFloat | SupportsComplex) -> bool:
        if not isinstance(value, Number):
            return self < Number(value)
        if self.numerator.imag or value.numerator.imag:
            return False
        return Fraction(self.numerator, self.denominator) < Fraction(
            value.numerator, value.denominator
        )

    def __le__(self, value) -> bool:
        return self < value or self == value

    @staticmethod
    def nth_root(x, n):
        if not isinstance(x, complex) and n % 2 == 1 and x < 0:
            return -abs(x) ** (1 / n)
        else:
            return x ** (1 / n)

    @dispatch
    def add(b, a):
        pass

    @add.register(number)
    def _(b, a):
        b = b.value
        if a.exp == b.exp == 1:
            return type(a)(value=a.value + b.value)
        return type(a)(a.coef + b.coef, a.value, a.exp)

    @dispatch
    def mul(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @mul.register(number)
    def _(b, a):
        b = b.value
        if a.like(b, 0):
            # Can be like term with different exponents (3^x * 3^y)
            if a.exp == b.exp:
                return type(a)(a.coef * b.coef, a.value * b.value, a.exp)
            return type(a)(a.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp))
        if a.exp == 1:
            return type(a)(a.value * b.coef, b.value, b.exp)
        if b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

    @staticmethod
    def resolve_pow(a, b):
        # NOTE: a^(nm) = (a^n)^m only if m is a real integer
        res = type(a)(a.coef, a.value) ** type(a)(b.tovalue())
        return type(a)(
            res.coef, res.value, type(a)(value=a.exp) * (b / type(a)(b.tovalue()))
        )

    @dispatch
    def pow(b, a):
        return Number.resolve_pow(a, b.value)

    @pow.register(number)
    def _(b, a):
        if a.exp == b.value.exp == 1:
            return type(a)(a.coef, a.value**b.value.value, a.exp)
        return Number.resolve_pow(a, b.value)

    pow.register(polynomial)(Base.poly_pow)
