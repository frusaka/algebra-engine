from __future__ import annotations
from functools import cached_property

from .collection import Collection
from utils import *
import itertools
from typing import TYPE_CHECKING, Sequence, Set

if TYPE_CHECKING:
    from .algebraobject import AlgebraObject


class Product(Collection):
    """A collection of unique terms that cannot be further be combined by multiplication or division"""

    def __new__(cls, objs: Sequence[AlgebraObject]) -> Product[AlgebraObject]:
        return super().__new__(cls, itertools.chain(*map(cls.flatten, objs)))

    def __str__(self) -> str:
        num, den = [], []
        for t in reversed(standard_form(self)):
            if t.exp_const() < 0:
                den.append(str(type(t)(value=t.value, exp=abs(t.exp))))
            else:
                num.append(str(t))
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
    def numerator(self) -> AlgebraObject:
        from .algebraobject import AlgebraObject

        res = AlgebraObject()
        for t in self:
            if t.exp_const() > 0:
                res *= t
        return res

    @cached_property
    def denominator(self) -> AlgebraObject:
        from .algebraobject import AlgebraObject

        res = AlgebraObject()
        for t in self:
            if t.exp_const() < 0:
                res *= t.inv
        return res

    @staticmethod
    def _mul(b: AlgebraObject, a: AlgebraObject) -> AlgebraObject:
        c = a.coef * b.coef
        res = a.value.simplify(type(a)(value=b.value, exp=b.exp))
        if res:
            if len(res) == 1:
                res = res.pop()
                return type(a)(c, res.value, res.exp)
            return type(a)(c, Product(res))
        return type(a)(value=c)

    @dispatch
    def add(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject | None:
        if a.like(b.value):
            return type(a)(a.coef + b.value.coef, a.value)

    @dispatch
    def mul(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject:
        return Product._mul(b.value, a)

    @mul.register(product)
    def _(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject:
        b = b.value
        if a.remainder.value and b.remainder.value:
            num = a.numerator * b.numerator
            den = a.denominator * b.denominator
            return num / den
        return Product._mul(a, b)

    @mul.register(number)
    def _(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject:
        if b.value.exp != 1:
            return
        return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial)
    def _(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject:
        b = b.value
        if abs(b.exp) != 1:
            return Product._mul(b, a)
        return b.value.mul(Proxy(a), b)

    @dispatch
    def pow(b: Proxy[AlgebraObject], a: AlgebraObject) -> AlgebraObject:
        res = type(a)()
        for i in a.value:
            res *= i**b.value
        return res * type(a)(value=a.coef) ** b.value

    @staticmethod
    def resolve(b: AlgebraObject, a: AlgebraObject) -> AlgebraObject:
        """Default multiplication fallback for incompatible values"""
        c = a.coef * b.coef
        a = type(a)(value=a.value, exp=a.exp)
        b = type(a)(value=b.value, exp=b.exp)
        return type(a)(c, Product([a, b]))

    def simplify(a, b: AlgebraObject) -> Set[AlgebraObject]:
        """Express a * b by combining like-terms"""
        # TODO: Implement canonical-based pairing
        objs = set(a)
        rem = set(b.value) if isinstance(b.value, Product) else {b}
        for a in tuple(objs):
            for b in tuple(rem):
                if not objs:
                    break
                if a.like(b, 0):
                    objs.remove(a)
                    rem.remove(b)
                    a *= b
                    if a.value != 1:
                        objs.add(a)
        return objs.union(rem)
