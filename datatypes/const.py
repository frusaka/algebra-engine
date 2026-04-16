from __future__ import annotations
import sys
import math
from typing import TYPE_CHECKING, Any


from .base import Node

from dataclasses import FrozenInstanceError
from functools import lru_cache

_PyHASH_MODULUS = sys.hash_info.modulus
_PyHASH_INF = sys.hash_info.inf
_HASH_IMAG = 1000003


@lru_cache(maxsize=1 << 14)
def _hash_algorithm(numerator, denominator):
    if numerator.imag:
        # Python's hash(c) = hash(real) + HASH_IMAG * hash(imag)
        return _hash_algorithm(
            numerator.real, denominator
        ) + _HASH_IMAG * _hash_algorithm(numerator.imag, denominator)
    # ***From https://github.com/python/cpython/blob/main/Lib/fractions.py***
    # To make sure that the hash of a Fraction agrees with the hash
    # of a numerically equal integer, float or Decimal instance, we
    # follow the rules for numeric hashes outlined in the
    # documentation.  (See library docs, 'Built-in Types').
    try:
        dinv = pow(denominator, -1, _PyHASH_MODULUS)
    except ValueError:
        # ValueError means there is no modular inverse.
        hash_ = _PyHASH_INF
    else:
        hash_ = hash(hash(abs(numerator)) * dinv)
    result = hash_ if numerator >= 0 else -hash_
    return -2 if result == -1 else result


class Number(Node):
    def __setattr__(self, name, value):
        raise FrozenInstanceError(f"cannot assign to field '{name}'")

    def __delattr__(self, name):
        raise FrozenInstanceError(f"cannot delete field '{name}'")

    def canonical(self):
        return (self, None)


class Complex:
    __slots__ = ("real", "imag")

    @lru_cache(maxsize=500)
    def __new__(cls, real: int = 0, imag: int = 0) -> Complex | complex | float | int:
        if int(real) != real or int(imag) != imag:
            if not imag:
                return real
            return complex(real, imag)
        real, imag = int(real), int(imag)
        if not imag:
            return real
        self = super(Complex, cls).__new__(cls)
        object.__setattr__(self, "real", real)
        object.__setattr__(self, "imag", imag)
        return self

    if TYPE_CHECKING:

        def __init__(self, real: int = 0, imag: int = 0): ...

    def __setattr__(self, name, value):
        raise FrozenInstanceError(f"cannot assign to field '{name}'")

    def __delattr__(self, name):
        raise FrozenInstanceError(f"cannot delete field '{name}'")

    def __repr__(self) -> str:
        r = str(self.real)
        i = str(self.imag) + "i"
        if abs(self.imag) == 1:
            i = i.replace("1i", "i")
        if not self.real:
            return i
        op = "" if i.startswith("-") else "+"
        return (r + op + i).join("()")

    def __complex__(self):
        return complex(float(self.real), float(self.imag))

    def __float__(self) -> float:
        if self.imag == Const(0):
            return float(self.real)
        raise ValueError("can't convert complex to float")

    def __bool__(self) -> bool:
        return bool(self.real) or bool(self.imag)

    def __hash__(self):
        return _hash_algorithm(self.real, 1) + _HASH_IMAG * _hash_algorithm(
            self.imag, 1
        )

    def __eq__(self, value: Any) -> bool:
        if value.__class__ not in {Complex, Const, int}:
            return False
        if value.__class__ is Complex:
            return self.real == value.real and self.imag == value.imag
        return self.real == value and self.imag == 0

    def __add__(self, other):
        return Complex(self.real + other.real, self.imag + other.imag)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return Complex(self.real - other.real, self.imag - other.imag)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        a, b = self.real, self.imag
        c, d = other.real, other.imag
        return Complex(a * c - b * d, a * d + b * c)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        a, b = self.real, self.imag
        c, d = other.real, other.imag
        denom = c * c + d * d
        return Complex((a * c + b * d) / denom, (b * c - a * d) / denom)

    def __rtruediv__(self, other):
        return Complex(other) / self

    def __pow__(self, other):
        assert type(other) is int and other >= 0
        if other == 0:
            return 1
        res = 1
        for _ in range(other):
            res *= self
        return res

    def __neg__(self):
        return Complex(-self.real, -self.imag)

    def conjugate(self):
        return Complex(self.real, -self.imag)


class Const(Number):
    """
    A repsentation of a numeric value.
    The `numerator` attribute can be an integer or a complex number.
    If the numerator is complex, the real and imaginary components will be whole numbers.
    The `denominator` attribute is always a positive integer.
    """

    __slots__ = ("numerator", "denominator")

    @lru_cache(maxsize=500)
    def __new__(cls, numerator: int | Complex = 0, denominator: int = 1) -> Const:
        if denominator == 0:
            raise ZeroDivisionError(f"{numerator}/{denominator}")
        if numerator.__class__ in {complex, Complex} and numerator.imag:
            rn, rd = numerator.real.as_integer_ratio()
            in_, id_ = numerator.imag.as_integer_ratio()
            d = math.lcm(rd, id_)
            real = d * rn // rd
            imag = d * in_ // id_
            denominator *= d
            if (gcd := math.gcd(denominator, real, imag)) != 1:
                real //= gcd
                imag //= gcd
                denominator //= gcd
            numerator = Complex(real, imag)
        else:
            if not isinstance(numerator, int):
                numerator, d = numerator.real.as_integer_ratio()
                denominator *= d
            if (gcd := math.gcd(denominator, numerator)) != 1:
                numerator //= gcd
                denominator //= gcd
        if denominator < 0:
            numerator *= -1
            denominator *= -1
        self = super(Const, cls).__new__(cls)
        object.__setattr__(self, "numerator", numerator)
        object.__setattr__(self, "denominator", denominator)
        return self

    if TYPE_CHECKING:

        def __init__(
            self, numerator: int | complex | str = 0, denominator: int = 1
        ): ...

    def __hash__(self) -> int:
        return _hash_algorithm(self.numerator, self.denominator)

    def __copy__(self) -> Const:
        cls = type(self)
        obj = super(Const, cls).__new__(cls)
        object.__setattr__(obj, "numerator", self.numerator)
        object.__setattr__(obj, "denominator", self.denominator)
        return obj

    def __float__(self) -> float:
        return self.numerator / self.denominator

    def __complex__(self):
        return complex(self.numerator / self.denominator)

    def __bool__(self) -> bool:
        return bool(self.numerator)

    def __repr__(self) -> str:
        # Lazy print
        return (
            str(self.numerator)
            if self.denominator == 1
            else f"{self.numerator}/{self.denominator}"
        )

    def __floor__(a) -> int:
        return a.numerator // a.denominator

    def __floordiv__(a, b: Const) -> int:
        return (a.numerator * b.denominator) // (a.denominator * b.numerator)

    def __mod__(a, b: Const) -> Const:
        da, db = a.denominator, b.denominator
        return Const((a.numerator * db) % (b.numerator * da), da * db)

    def as_ratio(self) -> tuple[Const]:
        return (Const(self.numerator), Const(self.denominator))

    def is_neg(self) -> bool:
        if self.numerator.imag:
            return False
        return self.numerator < 0

    def approx(self) -> float | complex:
        return self.numerator / self.denominator

    def add(self, value: Const) -> Const:
        if value.__class__ is Float:
            return value.add(self)
        den = math.lcm(self.denominator, value.denominator)
        return Const(
            (den // self.denominator) * self.numerator
            + (den // value.denominator) * value.numerator,
            den,
        )

    def mul(self, value: Const) -> Const:
        if value.__class__ is Float:
            return value.mul(self)
        return Const(
            self.numerator * value.numerator, self.denominator * value.denominator
        )

    def div(self, value: Const) -> Const:
        if value.__class__ is Float:
            return value.pow(-1).mul(self)
        num = self.numerator * value.denominator
        den = self.denominator * value.numerator
        if den.imag:
            conjugate = den.conjugate()
            den *= conjugate
            num *= conjugate
        return Const(num, den)

    def pow(self, value: int) -> Const:
        if value < 0:
            return Const(1).div(self.pow(-value))
        num = self.numerator**value
        den = self.denominator**value
        return Const(num, den)

    def __abs__(self) -> Const:
        return Const(abs(self.numerator), self.denominator)

    def __neg__(self) -> Const:
        return Const(-self.numerator, self.denominator)

    def __eq__(self, value: Any) -> bool:
        if value.__class__ not in {Const, int}:
            return False
        return (
            self.numerator == value.numerator and self.denominator == value.denominator
        )

    def __gt__(a, b: Const) -> bool:
        return a.numerator * b.denominator > a.denominator * b.numerator

    def __ge__(a, b: Const) -> bool:
        return a.numerator * b.denominator >= a.denominator * b.numerator

    def __lt__(a, b: Const) -> bool:
        return a.numerator * b.denominator < a.denominator * b.numerator

    def __le__(a, b: Const) -> bool:
        return a.numerator * b.denominator <= a.denominator * b.numerator

    def totex(self) -> str:
        n, *d = str(self).split("/")
        n = n.replace("i", "\\mathrm{i}")
        if not d:
            return n
        n = n.join("{}")
        d = d[0].join("{}")
        return f"\\frac{n}{d}"


class Float(Number):
    __slots__ = ("_val",)

    @lru_cache
    def __new__(cls, value: float | complex) -> Float:
        if isinstance(value, Node):
            value = value.approx()
        if abs(value.imag) <= 1e-10:
            value = value.real
        # c = Const(value)
        self = super(Float, cls).__new__(cls)
        object.__setattr__(self, "_val", value)
        return self

    if TYPE_CHECKING:

        def __init__(self, value: float | complex): ...

    def __repr__(self) -> str:
        # return repr(self._val)
        if not self._val.imag:
            return repr(round(self._val, 4))
        return repr(
            complex(round(self._val.real, 4), round(self._val.imag, 4))
        ).replace("j", "i")

    def __hash__(self) -> int:
        return hash(self._val)

    def __copy__(self) -> Float:
        cls = type(self)
        obj = super(Float, cls).__new__(cls)
        object.__setattr__(self, "_val", self._val)
        return obj

    def __abs__(self) -> Float:
        return Float(abs(self._val))

    def __float__(self) -> float:
        return float(self._val)

    def __complex__(self) -> complex:
        return complex(self._val)

    def __eq__(a, b: Any) -> bool:
        if not isinstance(b, (Const, int, Float)):
            return False
        if not isinstance(b, Float):
            b = Float(b)
        return a._val == b._val

    def __gt__(a, b: Number) -> bool:
        if not b.__class__ is Float:
            b = Float(b)
        return a._val > b._val

    def __ge__(a, b: Number) -> bool:
        if not b.__class__ is Float:
            b = Float(b)
        return a._val >= b._val

    def __lt__(a, b: Number) -> bool:
        if not b.__class__ is Float:
            b = Float(b)
        return a._val < b._val

    def __le__(a, b: Number) -> bool:
        if not b.__class__ is Float:
            b = Float(b)
        return a._val <= b._val

    def add(self, value: Number) -> Float:
        if not isinstance(value, Float):
            value = Float(value)
        return Float(self._val + value._val)

    def mul(self, value: Number) -> Float:
        if not isinstance(value, Float):
            value = Float(value)
        return Float(self._val * value._val)

    def div(self, value: Number) -> Float:
        if not isinstance(value, Float):
            value = Float(value)
        return Float(self._val / value._val)

    def pow(self, value: Number) -> Float:
        if (
            isinstance(value, Const)
            and value.denominator > 1
            and value.denominator % 2
            and self.is_neg()
        ):
            return Float(-abs(self._val) ** value.approx())
        if not isinstance(value, Float):
            value = Float(value)
        return Float(self._val**value._val)

    def is_neg(self) -> bool:
        if self._val.imag:
            return False
        return self._val < 0

    def approx(self) -> float | complex:
        return self._val

    def totex(self) -> str:
        return str(self).replace("i", "\\mathrm{i}")


__all__ = ["Complex", "Const", "Float"]
