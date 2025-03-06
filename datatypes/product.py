from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Set, Tuple

import itertools

from .collection import Collection
from functools import cached_property
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Product(Collection):
    """A collection of unique terms that cannot be further be combined by multiplication or division"""

    def __new__(cls, objs: Sequence[Term]) -> Product[Term]:
        return super().__new__(cls, itertools.chain(*map(cls.flatten, objs)))

    def __str__(self) -> str:
        num, den = [], []
        for t in reversed(standard_form(self)):
            if t.exp_const() < 0:
                den.append(str(type(t)(value=t.value, exp=-t.exp)))
            else:
                num.append(str(t))
            if str(t)[0].isdigit():
                num[-1] = num[-1].join("()")
        a, b = "".join(num), "".join(den)
        if len(num) > 1 and den:
            a = a.join("()")
        if "(" in b and len(den) > 1:
            b = b.join("()")
        if not num:
            return f"1/{b}"
        if den:
            return f"{a}/{b}"
        return a

    @cached_property
    def numerator(self) -> Term:
        from .term import Term

        res = Term()
        for t in self:
            if t.exp_const() > 0:
                res *= t
        return res

    @cached_property
    def denominator(self) -> Term:
        from .term import Term

        res = Term()
        for t in self:
            if t.exp_const() < 0:
                res *= t.inv
        return res

    @staticmethod
    def _mul(b: Term, a: Term) -> Term:
        from .polynomial import Polynomial

        # Expanding fractional polynomials
        if isinstance(a.denominator.value, Polynomial) or isinstance(
            b.denominator.value, Polynomial
        ):
            num = a.numerator * b.numerator
            den = a.denominator * b.denominator
            num, den = a.rationalize(num, den)
            return Product.resolve(num, den.inv)

        c, res = a.value.simplify(b.canonical())
        c *= a.to_const() * b.to_const()
        if res:
            if len(res) == 1:
                res = res.pop()
                return type(a)(c, res.value, res.exp)
            return type(a)(c, Product(res))
        return type(a)(value=c)

    @dispatch
    def add(b: Proxy[Term], a: Term) -> Term | None:
        if a.like(b.value):
            return type(a)(a.coef + b.value.coef, a.value)

    @dispatch
    def mul(b: Proxy[Term], a: Term) -> Term:
        return Product._mul(b.value, a)

    @mul.register(product)
    def _(b: Proxy[Term], a: Term) -> Term:
        b = b.value
        if a.remainder.value and b.remainder.value:
            num = a.numerator * b.numerator
            den = a.denominator * b.denominator
            return num / den
        return Product._mul(a, b)

    @mul.register(polynomial)
    def _(b: Proxy[Term], a: Term) -> Term:
        b = b.value
        if abs(b.exp) != 1:
            return Product._mul(b, a)
        return b.value.mul(Proxy(a), b)

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> Term:
        res = type(a)()
        for i in a.value:
            res *= i**b.value
        return res * type(a)(value=a.coef) ** b.value

    @staticmethod
    def resolve(b: Term, a: Term) -> Term:
        """Default multiplication fallback for incompatible values"""
        c = a.coef * b.coef
        a = type(a)(value=a.value, exp=a.exp)
        b = type(a)(value=b.value, exp=b.exp)
        return type(a)(c, Product([a, b]))

    def simplify(a, b: Term) -> Tuple[Number, Set[Term]]:
        """Express a * b by combining like-terms"""
        from .number import Number

        # TODO: Implement canonical-based pairing
        objs = set(a)
        c = Number(1)
        if b.value == 1:
            return c, objs
        rem = set(b.value) if isinstance(b.value, Product) else {b}
        for a in tuple(objs):
            for b in tuple(rem):
                if not objs:
                    break
                if a.like(b, 0):
                    objs.remove(a)
                    rem.remove(b)
                    a *= b
                    if a.to_const() != 1:
                        c *= a.to_const()
                        a = a.canonical()
                    if a.value != 1:
                        objs.add(a)
        return c, objs.union(rem)
