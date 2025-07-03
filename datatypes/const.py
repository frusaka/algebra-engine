from __future__ import annotations
import sys
import math
from typing import TYPE_CHECKING, Any

from utils.print_ import print_frac

from .base import Node

from fractions import Fraction
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


class Const(Node):
    """
    A repsentation of a numeric value.
    The `numerator` attribute can be an integer or a complex number.
    If the numerator is complex, the real and imaginary components will be whole numbers.
    The `denominator` attribute is always a positive integer.
    """

    numerator: int | complex
    denominator: int

    __slots__ = ("numerator", "denominator")

    @lru_cache
    def __new__(
        cls,
        numerator: int | complex | str = 0,
        denominator: int = 1,
    ) -> Const:
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

        self = super(Const, cls).__new__(cls)
        object.__setattr__(self, "numerator", numerator)
        object.__setattr__(self, "denominator", denominator)
        return self

    if TYPE_CHECKING:

        def __init__(
            self, numerator: int | complex | str = 0, denominator: int = 1
        ): ...

    def __setattr__(self, key, value):
        raise FrozenInstanceError(f"cannot assign to field '{key}'")

    def __delattr__(self, key):
        raise FrozenInstanceError(f"cannot delete field '{key}'")

    def __hash__(self):
        return _hash_algorithm(self.numerator, self.denominator)

    def __float__(self) -> float:
        return self.numerator / self.denominator

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

    def add(self, value: Const) -> Const:
        den = math.lcm(self.denominator, value.denominator)
        return Const(
            (den // self.denominator) * self.numerator
            + (den // value.denominator) * value.numerator,
            den,
        )

    def mul(self, value: Const) -> Const:
        return Const(
            self.numerator * value.numerator, self.denominator * value.denominator
        )

    def div(self, value: Const) -> Const:
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

    def canonical(self):
        return (self, None)

    def as_numer_denom(self) -> tuple[Node]:
        return (Const(self.numerator), Const(self.denominator))

    def approx(self) -> float | complex:
        return self.numerator / self.denominator


__all__ = ["Const"]
