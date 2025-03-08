from __future__ import annotations
from typing import Generator, Sequence, TYPE_CHECKING
from collections import defaultdict
from functools import cache, cached_property, lru_cache
import itertools
from .bases import Atomic
from .collection import Collection
from .number import Number, Fraction
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Polynomial(Collection):
    """A collection of unique terms that cannot be further be combined by addition or subtraction"""

    def __new__(cls, objs: Sequence[Term]) -> Polynomial:
        return super().__new__(cls, cls.merge(itertools.chain(*map(cls.flatten, objs))))

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
            return type(a)(value=Number(0))
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
        if a.exp == 1:
            res = Polynomial(t * b for t in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return next(iter(res))
            return type(a)(value=res)

        # Combining like terms
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )
        if b.value.__class__ is Polynomial and b.exp == 1:
            return b * a
        if a.exp == b.exp:
            return (
                (type(a)(value=a.value) * type(a)(value=b.value))
                ** type(a)(value=a.exp)
            ).scale(a.coef * b.coef)

        # Multiplication with a fraction Polynomial
        if a.exp == -1:
            num, den = a.rationalize(b, a.inv)
            if num.value.__class__ is Polynomial:
                return num / den  # -> Will perform long division
            if num.value.__class__ is Number and num.exp == 1:
                return type(a)(num.value, den.value, a.exp)
            return Product.resolve(num, den.inv)

        # Scalar multiplication
        if b.value.__class__ is Number and b.exp == 1:
            return a.scale(b.value)

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

    @cache
    def gcd(self) -> Term:
        """GCD of a polynomial. Ignores the coefficients"""
        terms = iter(self)
        gcd = next(terms)
        for i in terms:
            gcd = i.gcd(gcd, i)
        return gcd.canonical()

    @staticmethod
    def _long_division(a: Term, b: Term) -> Term:
        """
        Backend long division algorithm. `a` must have a higher degree than `b`.
        Returns Q -> Quotient, r -> remainder
        """

        org, q, r = a, [], None
        leading_b = b if b.value.__class__ is not Polynomial else b.value.leading

        while a.value:
            # Remainder
            if not a.value.__class__ is Polynomial or a.exp != 1:
                if (
                    not b.value.__class__ is Polynomial
                    and not (fac := a / b).remainder.value
                ):
                    q.append(fac)
                else:
                    r = a
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
                    r = org
                else:
                    r = a
                break
            q.append(fac)
            a -= b * fac
        return q, r

    @staticmethod
    def long_division(a: Term, b: Term, mixed=True) -> Term:
        """
        Perform Polynomial division on `a` with `b`, no matter which one has a higher degree.
        """
        from .product import Product

        if not a.value.__class__ is Polynomial:
            return a * b.inv

        if a.exp != 1 and a.exp == b.exp:
            return (
                Polynomial.long_division(type(a)(value=a.value), type(b)(value=b.value))
                ** type(a)(value=a.exp)
            ).scale(a.coef / b.coef)

        if a.exp != 1 or not b.exp.__class__ is Number:
            if b.value.__class__ is Number and b.exp == 1:
                return a.scale(b.inv.value)
            return Product.resolve(a, b.inv)

        # Inverse division
        if b.value.__class__ is Polynomial and lexicographic_weight(
            b.value.leading, 0
        ) > lexicographic_weight(a.value.leading, 0):
            res = Polynomial.long_division(b, a, 0)
            n, d = res.numerator, res.denominator
            if d.value == 1:
                return n.inv
            return Product.resolve(d, n.inv)

        q, r = Polynomial._long_division(a, b)
        if not q:
            return Product.resolve(a, b.inv)

        if len(q) == 1:
            q = q[0]
        else:
            q = type(a)(value=Polynomial(q))
        if not r:
            return q
        d = b
        if r.value.__class__ is Polynomial:
            # Super-simplification of remainders
            n, r2 = Polynomial._long_division(b, r)
            if r2 is None:
                r = type(a)(value=Polynomial(n)).inv
            else:
                # No Common factor cancelled
                if not mixed:
                    return Product.resolve(a, b.inv)
                r = Product.resolve(r, b.inv)
        else:
            # No Common factor cancelled
            if not mixed:
                return Product.resolve(a, b.inv)
            r /= b
        # Rewrite Q + r/d as N/D
        if not mixed:
            d = r.denominator
            r = r.numerator
            n, d = d.rationalize(q * d + r, d)
            return Product.resolve(n, d.inv)
        return q + r

    @staticmethod
    def merge(objs: Sequence[Term]) -> Generator[Term, None, None]:
        """Detect and combine like terms. All Symbolic fractions are combined into one as the remainder"""
        from .term import Term

        res = defaultdict(Number)
        fracs = defaultdict(Number)

        for t in objs:
            if t.value == 0:
                continue
            # Symbolic fractions
            if not t.denominator.value.__class__ is Number or t.denominator.exp != 1:
                fracs[t.canonical()] += t.to_const()
            else:
                res[t.canonical()] += t.to_const()
        # One remainder
        if len(fracs) == 1:
            k, v = fracs.popitem()
            res[k] += v

        # Multiple Symbolic fractions
        elif len(fracs) > 1:
            num = defaultdict(Number)
            vals = set()
            den = Term()

            # Compute the lcm of the fractions
            for k, v in fracs.items():
                den = den.lcm(den, k.denominator)
                vals.add(k.scale(v))

            # Compute the new numerator of each fraction
            for t in vals:
                t = (den / t.denominator) * t.numerator
                num[t.canonical()] += t.to_const()

            # A hashtable was used to prevent excessive recursion
            num = Term(value=Polynomial(k.scale(v) for k, v in num.items()))

            # Combine with the rest of the results
            if num.value:
                for t in Polynomial.flatten(num / den):
                    res[t.canonical()] += t.to_const()

        # Return them back into Term form and ignore 0's
        return (k.scale(v) for k, v in res.items() if v != 0)
