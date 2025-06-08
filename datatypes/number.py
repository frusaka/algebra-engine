from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
from pydoc import resolve
from typing import Any, SupportsFloat, SupportsComplex, TYPE_CHECKING
from .bases import Atomic, Fraction
from utils import *

if TYPE_CHECKING:
    from .term import Term


@dataclass(frozen=True, init=False)
class Number(Atomic):
    """
    A repsentation of a numeric value.
    The `numerator` attribute can be an integer or a complex number.
    If the numerator is complex, the real and imaginary components will be whole numbers.
    The `denominator` attribute is always an integer.
    """

    numerator: SupportsFloat | SupportsComplex | str
    denominator: SupportsFloat

    @lru_cache
    def __new__(
        cls,
        numerator: SupportsFloat | SupportsComplex | str = 0,
        denominator: SupportsFloat = 1,
    ) -> Number:
        obj = super().__new__(cls)
        if numerator.__class__ is complex and numerator.imag:
            if (
                gcd := math.gcd(denominator, int(numerator.real), int(numerator.imag))
            ) != 1:
                numerator /= gcd
                denominator //= gcd
        else:
            if numerator.__class__ is complex:
                numerator = numerator.real
            val = Fraction(numerator) / denominator
            numerator = val.numerator
            denominator = val.denominator
        object.__setattr__(obj, "numerator", numerator)
        object.__setattr__(obj, "denominator", denominator)
        object.__setattr__(obj, "_hash", hash((numerator, denominator)))
        return obj

    def __hash__(self):
        return self._hash

    def __float__(self) -> float:
        return self.numerator / self.denominator

    def __bool__(self) -> bool:
        return bool(self.numerator)

    def __repr__(self) -> str:
        # Lazy print
        res = print_frac(self).replace("j", "i")
        # Python quirk: -(1j) -> (-0-1j): (0-1j) -> 1j
        if res.startswith("(-0-"):
            res = res[3:-1]
        if abs(self.numerator.imag) == 1:
            return res.replace("1i", "i")
        return res

    def __add__(self, value: Number) -> Number:
        if not value.__class__ is Number:
            value = Number(value)
        den = math.lcm(self.denominator, value.denominator)
        return Number(
            (den // self.denominator) * self.numerator
            + (den // value.denominator) * value.numerator,
            den,
        )

    def __sub__(self, value: Number) -> Number:
        return self + -value

    def __mul__(self, value: Number) -> Number:
        return Number(
            self.numerator * value.numerator, self.denominator * value.denominator
        )

    def __truediv__(self, value: Number) -> Number:
        num = self.numerator * value.denominator
        den = self.denominator * value.numerator
        if den.imag:
            conjugate = complex(den.real, -den.imag)
            num *= conjugate
            den *= conjugate
            return Number(num, int(den.real))
        return Number(num, den)

    def __pow__(self, value: Number) -> Number:
        if value.numerator < 0:
            return Number(1) / (self**-value)
        # Needs saftey checks. The numerator can be too large.
        num = self.numerator**value.numerator
        den = self.denominator**value.numerator
        if value.denominator != 1:
            num = self.nth_root(num, value.denominator)
            den = self.nth_root(den, value.denominator)
            if num.imag:
                num = complex(round(num.real, 10), round(num.imag, 10))
            if den.imag:
                den = complex(round(den.real, 10), round(den.imag, 10))
        return Number(num) / Number(den)

    def __abs__(self) -> Number:
        return Number(abs(self.numerator), self.denominator)

    def __neg__(self) -> Number:
        return Number(-self.numerator, self.denominator)

    def __eq__(self, value: Any) -> bool:
        if value.__class__ not in {Number, int}:
            return False
        return (
            self.numerator == value.numerator and self.denominator == value.denominator
        )

    def __gt__(self, value: Number) -> bool:
        if self.numerator.imag or value.numerator.imag:
            return False
        den = math.lcm(self.denominator, value.denominator)
        return (den // self.denominator * self.numerator) > (
            den // value.denominator * value.numerator
        )

    def __lt__(self, value: Number) -> bool:
        if self.numerator.imag or value.numerator.imag:
            return False
        den = math.lcm(self.denominator, value.denominator)
        return (den // self.denominator * self.numerator) < (
            den // value.denominator * value.numerator
        )

    @staticmethod
    def nth_root(x: SupportsFloat | SupportsComplex, n: int) -> float:
        if not x.__class__ is complex and n % 2 == 1 and x < 0:
            return -abs(x) ** (1 / n)
        else:
            return x ** (1 / n)

    @dispatch
    def add(b: Proxy[Term], a: Term) -> None:
        b = b.value
        if a.exp == b.exp == 1:
            return type(a)(value=a.value + b.value)
        return type(a)(a.coef + b.coef, a.value, a.exp)

    @dispatch
    def mul(b: Proxy[Term], a: Term) -> Term | None:
        return b.value.value.mul(Proxy(a), b.value)

    @mul.register(number)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        b = b.value
        if a.like(b, 0):
            # Can be like term with different exponents (3^x * 3^y)
            c = a.coef * b.coef
            # Radicals that are left as is to preserve accuracy
            if (
                (a.exp != 1 or b.exp != 1)
                and a.exp.__class__ is Number
                and b.exp.__class__ is Number
            ):
                if a.value == b.value:
                    exp = a.exp + b.exp
                    return simplify_radical(a.value**exp.numerator, exp.denominator, c)
                if a.exp != b.exp:
                    exp = math.lcm(a.exp.denominator, b.exp.denominator)
                    return simplify_radical(
                        a.value ** (exp // a.exp.denominator)
                        * b.value ** (exp // b.exp.denominator),
                        exp,
                        c,
                    )
                return simplify_radical(a.value * b.value, a.exp.denominator, c)
            if a.exp == b.exp:
                return type(a)(c, a.value * b.value, a.exp)
        if a.exp == 1:
            return type(a)(a.value * b.coef, b.value, b.exp)
        if b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)
        # Put last to prevent combining cases such as 3*3^x
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )

    @staticmethod
    def resolve_pow(a: Term, b: Term) -> Term:
        if a.coef != 1:
            return Number.resolve_pow(type(a)(a.coef), b) * Number.resolve_pow(
                type(a)(value=a.value, exp=a.exp), b
            )
        c = type(a)(a.value) ** type(a)(b.to_const())
        e = type(a)(value=a.exp) * b.canonical()
        return type(a)(c.coef, c.value, e)

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> Term:
        return Number.resolve_pow(a, b.value)

    @pow.register(number)
    def _(b: Proxy[Term], a: Term) -> Term:
        b = b.value
        if b.exp == 1 and a.exp.__class__ is Number:
            b = b.value
            c = a.coef**b.numerator
            exp_a = a.exp * b
            v = a.value**exp_a.numerator
            if exp_a.denominator == b.denominator == 1:
                return type(a)(c * v)
            # Leave radicals as is if necessary to maintain precision
            return simplify_radical(v, exp_a.denominator) * simplify_radical(
                c, b.denominator
            )
        return Number.resolve_pow(a, b)

    pow.register(polynomial)(Atomic.poly_pow)

    def ast_subs(self, mapping: dict):
        return self

    def totex(self) -> str:
        if "/" in (s := str(self).replace("i", "\\mathrm{i}")):
            num, den = s.split("/")
            return "\\frac{0}{1}".format(num.join("{}"), den.join("{}"))
        return s
