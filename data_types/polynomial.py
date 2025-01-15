from __future__ import annotations
from collections import defaultdict
from functools import cache, cached_property
import itertools
from .collection import Collection
from .number import Number
from utils import *
from typing import Generator, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from .algebraobject import AlgebraObject


class Polynomial(Collection):
    def __new__(cls, objs: Sequence[AlgebraObject]) -> Polynomial:
        return super().__new__(cls, cls.merge(itertools.chain(*map(cls.flatten, objs))))

    def __str__(self):
        res = ""
        for idx, algebraobject in enumerate(standard_form(self)):
            rep = str(algebraobject)
            if idx > 0 and res:
                if rep.startswith("-"):
                    rep = rep[1:]
                    res += " - "
                else:
                    res += " + "
            res += rep
        return res.join("()")

    @staticmethod
    def resolve(b: Proxy[AlgebraObject], a: AlgebraObject):
        val = Polynomial([b.value, a])
        if not val:
            return type(a)(value=Number(0))
        if len(val) == 1:
            return next(iter(val))
        return type(a)(value=val)

    @dispatch
    def add(b: Proxy[AlgebraObject], a: AlgebraObject):
        return Polynomial.resolve(b, a)

    @add.register(polynomial)
    def _(b: Proxy[AlgebraObject], a: AlgebraObject):
        if a.like(b.value) and a.exp != 1:
            return type(a)(a.coef + b.value.coef, a.value, a.exp)
        return Polynomial.resolve(b, a)

    @dispatch
    def mul(b: Proxy[AlgebraObject], a: AlgebraObject):
        from .product import Product

        b = b.value
        if a.exp == 1:
            res = Polynomial(t * b for t in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return next(iter(res))
            return type(a)(value=res)
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )
        if isinstance(b.value, Polynomial) and b.exp == 1:
            return b * a
        if a.exp == -1:
            num, den = a.rationalize(b, a.inv)
            if isinstance(num.value, Polynomial):
                return num / den
            if isinstance(num.value, Number) and num.exp == 1:
                return type(a)(num.value, den.value, a.exp)
            return Product.resolve(num, den.inv)
        if isinstance(a.exp, Number) and isinstance(b.value, Number) and b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

    @cached_property
    def leading(self) -> AlgebraObject:
        return max(self, key=lexicographic_weight)

    @cache
    def leading_options(self) -> tuple[AlgebraObject]:
        leading = self.leading
        return tuple(
            i
            for i in self
            if lexicographic_weight(i, 0) == lexicographic_weight(leading, 0)
        )

    @staticmethod
    def _long_division(a: AlgebraObject, b: AlgebraObject) -> AlgebraObject:
        from .product import Product
        from .algebraobject import AlgebraObject

        if a.exp != 1 or b.exp != 1:
            return Product.resolve(a, b.inv)
        leading_b = b
        options_b = []
        if isinstance(b.value, Polynomial):
            options_b = list(b.value.leading_options())
            leading_b = options_b.pop()

        org = a
        res = AlgebraObject(Number(0))
        while a.value:
            # Remainder
            if not isinstance(a.value, Polynomial) or a.exp != 1:
                res += a * b.inv
                break
            for leading_a in a.value.leading_options():
                fac = leading_a / leading_b
                if (
                    isinstance(fac.denominator.value, Number)
                    and fac.denominator.exp == 1
                ):
                    break
            else:
                if not res.value and options_b:
                    leading_b = options_b.pop()
                    a = org
                    res = AlgebraObject(Number(0))
                    continue
                res += Product.resolve(a, b.inv)
                break
            res += fac
            a -= fac * b
        return res

    @staticmethod
    def long_division(a: AlgebraObject, b: AlgebraObject) -> AlgebraObject:
        # Supports dual direction long division
        from .product import Product

        if lexicographic_weight(b, 0) > lexicographic_weight(a, 0) and isinstance(
            b.value, Polynomial
        ):
            res = Polynomial._long_division(b, a)
            a, b = a.rationalize(type(a)(), res)
            if isinstance(a.value, Number) and a.exp == 1:
                return type(a)(a.value * b.coef, b.value, -b.exp)
            return Product.resolve(a, b.inv)
        return Polynomial._long_division(a, b)

    @staticmethod
    def merge(
        objs: Sequence[AlgebraObject],
    ) -> Generator[AlgebraObject]:
        from .algebraobject import AlgebraObject

        res = defaultdict(Number)
        fracs = defaultdict(Number)

        for t in objs:
            if t.value == 0:
                continue
            # Symbolic Fractions
            if not isinstance(t.denominator.value, Number) or t.denominator.exp != 1:
                fracs[t.canonical()] += t.to_const()
            else:
                res[t.canonical()] += t.to_const()
        if len(fracs) == 1:
            k, v = fracs.popitem()
            res[k] += v
        elif len(fracs) > 1:
            num = defaultdict(Number)
            vals = set()
            den = AlgebraObject()
            for k, v in fracs.items():
                t = k.scale(v)
                den = den.lcm(den, t.denominator)
                vals.add(t)
            for t in vals:
                t = (den / t.denominator) * t.numerator
                num[t.canonical()] += t.to_const()
            if len(num) == 1:
                k, v = num.popitem()
                num = k.lazyscale(v)
            else:
                num = AlgebraObject(
                    value=Polynomial(k.scale(v) for k, v in num.items() if v != 0)
                )
            for t in Polynomial.flatten(num / den):
                res[t.canonical()] += t.to_const()
        return (k.scale(v) for k, v in res.items() if v != 0)
