from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Set, Tuple

import itertools
from functools import cached_property, reduce
from .collection import Collection
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Product(Collection):
    """A collection of unique terms that cannot be further be combined by multiplication or division"""

    def __new__(cls, objs: Sequence[Term]) -> Product[Term]:
        return super().__new__(cls, itertools.chain(*map(cls.flatten, objs)))

    def __float__(self):
        return reduce(lambda a, b: a * b, map(float, self))

    def __repr__(self) -> str:
        num, den = [], []
        for t in reversed(standard_form(self)):
            if t.exp_const() < 0:
                den.append(repr(type(t)(value=t.value, exp=-t.exp)))
                if repr(t)[0].isdigit():
                    den[-1] = den[-1].join("()")
            else:
                num.append(repr(t))
                if repr(t)[0].isdigit():
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
                res *= Term(value=t.value, exp=-t.exp)
        return res

    @staticmethod
    def _mul(b: Term, a: Term) -> Term:
        from .polynomial import Polynomial

        # Expanding fractional polynomials
        if (
            (a.denominator.value.__class__ is Polynomial and a.denominator.exp == 1)
            or b.denominator.value.__class__ is Polynomial
            and b.denominator.exp == 1
        ):
            num = a.numerator * b.numerator
            den = a.denominator * b.denominator
            if num.value.__class__ is Polynomial:
                return Polynomial.long_division(num, den)
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
        from .number import Number

        c = Number(1)
        res = []
        for i in a.value | {type(a)(value=a.coef)}:
            i **= b.value
            if i.value.__class__ is Number and i.exp == 1:
                c *= i.value
            else:
                res.append(i)
        if len(res) == 1:
            return res.pop() * type(a)(c)
        if not res:
            return type(a)(c)
        return type(a)(c, Product(res))

    @staticmethod
    def resolve(a: Term, b: Term) -> Term:
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
        rem = set(b.value) if b.value.__class__ is Product else {b}
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

    def ast_subs(self, mapping: dict):
        from processing import Token, TokenType, Binary

        data = tuple(self)
        res = Binary(
            Token(TokenType.MUL), data[0].ast_subs(mapping), data[1].ast_subs(mapping)
        )
        for i in data[2:]:
            res = Binary(Token(TokenType.MUL), res, i.ast_subs(mapping))
        return res

    def totex(self) -> str:
        num, den = [], []
        wrap = False
        for t in reversed(standard_form(self)):
            if (
                t.value.__class__.__name__ == "Number"
                and t.exp.__class__.__name__ != "Number"
            ):
                wrap = True
            if t.exp_const() < 0:
                den.append(type(t)(value=t.value, exp=-t.exp).totex())
            else:
                num.append(t.totex())
        a, b = "".join(num).join("{}"), "".join(den).join("{}")
        if wrap:
            a = a.join("()")
        if not num:
            return f"\\frac{1}{b}"
        if den:
            return f"\\frac{a}{b}"
        return a
