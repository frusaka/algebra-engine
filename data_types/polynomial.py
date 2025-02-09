from __future__ import annotations
from collections import defaultdict
from functools import cache, cached_property
import itertools
from .bases import Atomic
from .collection import Collection
from .number import Number, Fraction
from utils import *
from typing import Generator, Sequence, TYPE_CHECKING

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
                    rep = str(-term)
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
        if isinstance(b.value, Polynomial) and b.exp == 1:
            return b * a

        # Multiplication with a fraction Polynomial
        if a.exp == -1:
            num, den = a.rationalize(b, a.inv)
            if isinstance(num.value, Polynomial):
                return num / den  # -> Will perform long division
            if isinstance(num.value, Number) and num.exp == 1:
                return type(a)(num.value, den.value, a.exp)
            return Product.resolve(num, den.inv)

        # Scalar multiplication
        if isinstance(b.value, Number) and b.exp == 1:
            return a.scale(b.value)

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> None:
        pass

    @pow.register(number)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        if a.exp == -1 and abs(b.value.value) != 1:
            return Polynomial.scalar_pow(b.value, type(a)(value=a.value)).inv
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
            if b.denominator == 1:
                num, den = type(a).rationalize(type(a)(), res)
                den = type(a)(value=den.value, exp=-den.exp)
                return num * den
            exp = -exp
        res = type(a)(value=res.value, exp=res.exp * exp)
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
            i
            for i in self
            if lexicographic_weight(i, 0) == lexicographic_weight(leading, 0)
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
        """Backend long division algorithm. `a` must have a higher degree than `b`"""
        from .product import Product
        from .term import Term

        if a.exp != 1 or not isinstance(b.exp, Number):
            if isinstance(b.value, Number) and b.exp == 1:
                return a.scale(b.inv.value)
            return Product.resolve(a, b.inv)
        leading_b = b
        options_b = []
        if isinstance(b.value, Polynomial):
            options_b = list(b.value.leading_options())
            leading_b = options_b.pop()

        org = a
        res = Term(Number(0))
        while a.value:
            # Remainder
            if not isinstance(a.value, Polynomial) or a.exp != 1:
                res += a * b.inv
                break
            for leading_a in a.value.leading_options():
                fac = leading_a / leading_b
                if not fac.remainder.value:
                    break
            else:
                if not res.value and options_b:
                    leading_b = options_b.pop()
                    a = org
                    res = Term(Number(0))
                    continue
                res += Product.resolve(a, b.inv)
                break
            res += fac
            a -= fac * b
        return res

    @staticmethod
    @cache
    def long_division(a: Term, b: Term) -> Term:
        """
        Perform Polynomial division on `a` with `b`, no matter which one has a higher degree.
        """
        from .product import Product

        if lexicographic_weight(b, 0) > lexicographic_weight(a, 0) and isinstance(
            b.value, Polynomial
        ):
            res = Polynomial._long_division(b, a)
            a, b = a.rationalize(type(a)(), res)
            if isinstance(a.value, Number) and a.exp == 1:
                return type(a)(a.value * b.coef, b.value, -b.exp)
            return Product.resolve(a, b.inv)
        res = Polynomial._long_division(a, b)
        # Basic super-simplification of remainders
        # E.g ((x-3)(x+3))/(x-3)^2 => 1 + 6/(x-3)
        if isinstance(res.remainder.value, Polynomial):
            rem = Polynomial._long_division(b, res.remainder)
            if rem.remainder.value == 0:
                rem = rem.inv
                res -= res.fractional
                res += rem
        return res

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
            if not isinstance(t.denominator.value, Number) or t.denominator.exp != 1:
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
                t = k.scale(v)
                den = den.lcm(den, t.denominator)
                vals.add(t)

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
