from __future__ import annotations
from abc import ABC, abstractmethod
import numbers
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


class Const(Number):
    """
    A repsentation of a numeric value.
    The `numerator` attribute can be an integer or a complex number.
    If the numerator is complex, the real and imaginary components will be whole numbers.
    The `denominator` attribute is always a positive integer.
    """

    __slots__ = ("numerator", "denominator")

    @lru_cache(maxsize=500)
    def __new__(cls, numerator: int | complex = 0, denominator: int = 1) -> Const:
        if denominator == 0:
            raise ZeroDivisionError(f"{numerator}/{denominator}")
        if numerator.__class__ is complex and numerator.imag:
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
            numerator = complex(real, imag)
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

    def __hash__(self):
        return _hash_algorithm(self.numerator, self.denominator)

    def __float__(self) -> float:
        return self.numerator / self.denominator

    def __complex__(self):
        return complex(self.numerator / self.denominator)

    def __bool__(self) -> bool:
        return bool(self.numerator)

    def __repr__(self) -> str:
        # Lazy print
        res = (
            str(self.numerator)
            if self.denominator == 1
            else f"{self.numerator}/{self.denominator}"
        ).replace("j", "i")
        # Python quirk: -(1j) -> (-0-1j): (0-1j) -> -1j
        if res.startswith("(-0-"):
            res = res[3:-1]
        if abs(self.numerator.imag) == 1:
            return res.replace("1i", "i")
        return res

    def __floor__(a):
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
            den = int((den * conjugate).real)
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

    def totex(self):
        n = str(self.numerator).replace("i", "\\mathrm{i}")
        if self.denominator == 1:
            return n
        n = n.join("{}")
        d = str(self.denominator).join("{}")
        return f"\\dfrac{n}{d}"


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

    def __repr__(self):
        # return repr(self._val)
        if not self._val.imag:
            return repr(round(self._val, 4))
        return repr(complex(round(self._val.real, 4), round(self._val.imag, 4)))

    def __hash__(self):
        return hash(self._val)

    def __abs__(self):
        return Float(abs(self._val))

    def __float__(self):
        return float(self._val)

    def __complex__(self):
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

    def is_neg(self):
        if self._val.imag:
            return False
        return self._val < 0

    def approx(self) -> float | complex:
        return self._val


__all__ = ["Const", "Float"]
