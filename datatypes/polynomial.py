from __future__ import annotations
from typing import Generator, Sequence, TYPE_CHECKING
from collections import defaultdict
from functools import cache, cached_property, lru_cache
import itertools
from .bases import Atomic
from .collection import Collection
from .number import Number, Fraction, ONE, ZERO
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Polynomial(Collection):
    """A collection of unique terms that cannot be further be combined by addition or subtraction"""

    def __new__(cls, objs: Sequence[Term], merge=True) -> Polynomial:
        if merge:
            objs = cls.merge(itertools.chain(*map(cls.flatten, objs)))
        return super().__new__(cls, objs)

    def __str__(self):
        res = ""
        for idx, term in enumerate(standard_form(self)):
            rep = str(term)
            if idx > 0 and res:
                # Needs fix to account for complex number or values like x + (-2x+3)/ab
                if rep.startswith("-"):
                    res += " - "
                    rep = rep[1:]
                else:
                    res += " + "
            res += rep
        return res.join("()")

    @staticmethod
    def resolve(b: Proxy[Term], a: Term):
        """A default fallback if two terms are not like"""
        val = Polynomial([b.value, a])
        if not val:
            return type(a)(value=ZERO)
        if len(val) == 1:
            return next(iter(val))
        return type(a)(value=val)

    @dispatch
    def add(b: Proxy[Term], a: Term):
        return Polynomial.resolve(b, a)

    @add.register(polynomial)
    def _(b: Proxy[Term], a: Term):
        if a.like(b.value) and a.exp != 1:
            return type(a)(a.coef + b.value.coef, a.value, a.exp)
        return Polynomial.resolve(b, a)

    @dispatch
    def mul(b: Proxy[Term], a: Term):
        from .product import Product

        b = b.value
        # Distributive property of Multiplication
        if b.value == ZERO:
            return type(a)(value=ZERO)
        if a.exp == 1:
            res = Polynomial((t * b for t in a.value))
            if len(res) == 1:
                return next(iter(res))
            return type(a)(value=res)

        # if a.exp == b.exp:
        #     return (
        #         (type(a)(value=a.value) * type(a)(value=b.value))
        #         ** type(a)(value=a.exp)
        #     ).scale(a.coef * b.coef)

        # Scalar multiplication
        if b.value.__class__ is Number and b.exp == 1:
            if a.exp == -1 and a.value.leading.to_const() < 0:
                return type(a)(
                    b.value * -a.coef,
                    Polynomial((x.scale(-1) for x in a.value), 0),
                    a.exp,
                )
            return a.scale(b.value)
        # Multiplication with a fraction Polynomial
        if (
            a.exp_const() < 0
            and b.value.__class__ is Product
            and b.value.numerator.value.__class__ is Polynomial
        ):
            return b.numerator / (a.inv * b.denominator)

    @mul.register(polynomial)
    def _(b: Proxy[Term], a: Term) -> None:
        b = b.value
        if a.exp == 1:
            if b.exp == 1:
                # Faster expansion
                return type(a)(
                    value=Polynomial(i * j for i in a.value for j in b.value)
                )
            if b.exp_const().numerator < 0:
                return a / b.inv
            return type(a)(value=Polynomial((i * b for i in a.value), 0))
        if b.exp == 1:
            return b * a
        # Combining like terms
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> None:
        pass

    @pow.register(number)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        if a.exp == -1 and abs(b.value.value) != 1:
            return (
                Polynomial.scalar_pow(b.value, type(a)(value=a.value)).inv
                * type(a)(value=a.coef) ** b.value
            )
        return Polynomial.scalar_pow(b.value, a)

    @staticmethod
    def scalar_pow(b: Term, a: Term) -> Term | None:
        """For-loop based exponentiation of a Polynomial"""

        if b.exp != 1 or a.exp != 1:
            if b.coef != 1:
                return (a ** type(a)(b.coef)) ** type(a)(b.value, exp=b.exp)
            return
        b = b.value
        if b.numerator.imag:
            return type(a)(
                a.coef**b.value, a.value, type(a)(value=a.exp) * type(a)(b.value)
            )
        res = a
        for _ in range(abs(b.numerator) - 1):
            res *= a
        exp = Fraction(1, b.denominator)
        if b < 0:
            exp = -exp
        if b.denominator != 1 or b < 0 and res.exp == 1:
            num, den = type(a).rationalize(res, type(a)())
            if num.value.__class__ is Polynomial:
                # Perfect square trinomials
                if b.denominator == 2 and (v := perfect_square(num.value)):
                    num = v
                    if exp < 0:
                        num = type(a)(value=num.value, exp=num.exp * exp.numerator)
                else:
                    num = type(a)(value=num.value, exp=num.exp * exp)
            else:
                num **= type(a)(Number(exp))
            return num * den ** type(a)(Number(-exp))
        return res

    pow.register(polynomial)(Atomic.poly_pow)

    @cached_property
    def leading(self) -> Term:
        return max(self, key=lexicographic_weight)

    @cache
    def leading_options(self) -> tuple[Term]:
        """Get all the the terms that have a degree equivalent to the leading term's degree"""
        leading = self.leading
        return tuple(
            reversed(
                standard_form(
                    i
                    for i in self
                    if lexicographic_weight(i, 0) == lexicographic_weight(leading, 0)
                )
            )
        )

    @lru_cache
    def gcd(self) -> Term:
        """GCD of a polynomial. Ignores the coefficients"""
        terms = iter(self)
        gcd = next(terms)
        for i in terms:
            gcd = i.gcd(gcd, i)
        return gcd.canonical()

    @staticmethod
    @lru_cache
    def _long_division(a: Term, b: Term) -> tuple:
        """
        Backend long division algorithm. `a` must have a higher degree than `b`.
        Returns Q -> Quotient, r -> remainder
        """

        org, q = a, []
        leading_b = b if b.value.__class__ is not Polynomial else b.value.leading

        while a.value:
            # Remainder
            if not a.value.__class__ is Polynomial or a.exp != 1:
                if (
                    not b.value.__class__ is Polynomial
                    and not (fac := a / b).remainder.value
                ):
                    q.append(fac)
                    a = type(a)(Number())
                break
            for leading_a in a.value.leading_options():
                if not (fac := leading_a / leading_b).remainder.value:
                    break
            else:
                # Has to be a non-terminating polynomial division
                # E.g (b^3 + ab)/(b - a) => (b^2 + a^2 + ab + (a^3 + ab)/(b - a))
                # The remainder gets a higher degree than the divisor, so leave as improper fraction instead
                if lexicographic_weight(leading_a, 0) > lexicographic_weight(
                    leading_b, 0
                ):
                    q = []
                    a = org
                break
            q.append(fac)
            a += -b * fac
        return q, a

    @staticmethod
    def long_division(a: Term, b: Term, combine=True) -> Term:
        """
        Perform Polynomial division on `a` with `b`, no matter which one has a higher degree.
        """
        from .product import Product

        if not a.value.__class__ is Polynomial:
            if not combine:
                return a, b
            return a * b.inv

        if a.exp != 1 or b.value.__class__ is Polynomial and b.exp != 1:
            if not combine:
                return a, b
            if b.value.__class__ is Number and b.exp == 1:
                return a.scale(b.inv.value)
            return Product.resolve(a, b.inv)

        # Inverse division
        if b.value.__class__ is Polynomial and lexicographic_weight(
            b.value.leading, 0
        ) > lexicographic_weight(a.value.leading, 0):
            n, d = Polynomial.long_division(b, a, 0)
            if not combine:
                return d, n
            if d.value == 1:
                return n.inv
            n, d = n.rationalize(n, d)
            return Product.resolve(d, n.inv)

        # Find common factor
        b2 = b
        a2 = a
        while b.value:
            q, r = Polynomial._long_division(a, b)
            if not q or r.value and r.value.__class__ is not Polynomial:
                if not combine:
                    return a2, b2
                a, b = a.rationalize(a2, b2)
                return Product.resolve(a, b.inv)
            a, b = b, r
        # Cancel common factor
        a2 = Polynomial._long_division(a2, a)[0]
        b = Polynomial._long_division(b2, a)[0]
        a = a2[0] if len(a2) == 1 else type(a)(value=Polynomial(a2, 0))
        b = b[0] if len(b) == 1 else type(a)(value=Polynomial(b, 0))

        if not combine:
            return a, b
        # Combine the simplified fraction
        if b.value.__class__ is not Number:
            a, b = a.rationalize(a, b)
            return Product.resolve(a, b.inv)
        return a * b.inv

    @staticmethod
    def merge(objs: Sequence[Term]) -> Generator[Term, None, None]:
        """Detect and combine like terms. All Symbolic fractions are combined into one as the remainder"""
        from .term import Term

        res = defaultdict(Number)
        frac = False

        for t in objs:
            if t.value == 0:
                continue
            res[t.canonical()] += t.to_const()
            # Symbolic fractions
            if t.remainder.value:
                frac = True

        # Multiple Symbolic fractions
        if frac and len(res) > 1:
            num = []
            den = Term()

            # Compute the lcm of the fractions
            for k in res:
                den = den if k.denominator._hash == den._hash else den * k.denominator
                # den *= k.denominator
                # den = den.lcm(den, k.denominator)

            # Compute the new numerator of each fraction
            for k, v in res.items():
                t = k.scale(v)
                t = (den / t.denominator) * t.numerator
                num.append(t)

            if num := Polynomial(num):
                yield from Polynomial.flatten(Term(value=num) / den)
            return
        # Return them back into Term form and ignore 0's
        yield from (k.scale(v) for k, v in res.items() if v != 0)

    def totex(self):
        res = ""
        for term in standard_form(self):
            rep = term.totex()
            if res:
                n = term.to_const().numerator
                if n.__class__ is complex and (not n.real and n.imag < 0) or n.real < 0:
                    res += "-"
                    rep = (-term).totex()
                else:
                    res += "+"
            res += rep
        return "\\left(" + res + "\\right)"
