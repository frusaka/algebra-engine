from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from functools import cache, cached_property, lru_cache
import math
from .number import Number
from .variable import Variable
from .collection import Collection
from .product import Product
from .polynomial import Polynomial
from utils import Proxy, print_coef, lexicographic_weight


@dataclass(frozen=True, init=False, order=True)
class Term:
    """
    A representation of a mathemetical term.
    The `coef` field represents the coefficient (2 in 2x).
    The `value` field represents the constant or unknown (x in 2x, 5 in 5)
    The `exp` field represents the exponent (2 in 3x^2). If the exponent is negative, then it is printed as a division
    """

    coef: Number
    value: Number | Variable | Product | Polynomial
    exp: Number | Term

    @lru_cache(maxsize=500)
    def __new__(cls, coef=Number(1), value=Number(1), exp=Number(1)) -> Term:
        if value.__class__ is Term:
            return value
        obj = super().__new__(cls)
        # Cases when operations with exponents simplify to a constant
        if exp.__class__ is Term and exp.value.__class__ is Number and exp.exp == 1:
            exp = exp.value
        # Aplying basic known algebraic rules to validate the term
        if coef == 0 or value == 0:
            value = Number(0)
            coef = exp = Number(1)
        elif coef != 1 and value == 1:
            value, coef = coef, value
            exp = coef
        elif exp == 0:
            value = coef
            exp = coef = Number(1)
        # # 1^n = 1 for any value of n
        elif value == 1:
            exp = value
        object.__setattr__(obj, "coef", coef)
        object.__setattr__(obj, "value", value)
        object.__setattr__(obj, "exp", exp)
        return obj

    def __str__(self) -> str:
        if (
            "/" in str(self.coef)
            or self.value.__class__ is Product
            and not self.denominator.value.__class__ is Number
        ):
            return "{0}/{1}".format(self.numerator, self.denominator)
        # Numbers with symbolic exponents
        if self.value.__class__ is Number and self.exp != 1:
            v = str(Term(value="$", exp=self.exp)).replace(
                "$", v if not "/" in (v := str(self.value)) else v.join("()")
            )
            if not v.startswith("(") and abs(self.coef) != 1:
                v = v.join("()")
            return "{0}{1}".format(print_coef(self.coef), v)
        # Negative exponets: ax^-n -> a/x^n
        if self.exp_const() < 0:
            return "{0}/{1}".format(self.numerator, self.denominator)
        res = print_coef(self.coef)
        # Cases when a Polynomial or Product has no variable numerator
        # Instead of 3(1/(abc)), prints 3/(abc)
        if (
            isinstance(self.value, Collection)
            and self.numerator.value.__class__ is Number
        ):
            if not res or res == "-":
                res = str(self.coef)
            res += "/" + str(self.denominator.value)
        else:
            res += str(self.value)
        if self.exp == 1:
            return res
        exp = self.exp_const()

        # Radical representation
        if exp.denominator != 1:
            if self.coef != 1:
                val = Term(value=self.value, exp=self.exp)
                if self.coef == -1:
                    return "-{0}".format(val)
                return "{0}({1})".format(print_coef(self.coef), val)
            if exp.numerator != 1:
                res = "{0}^{1}".format(res, exp.numerator)
            return "{0}√{1}".format(exp.denominator, res)

        # Symbolic exponent representation
        exp = str(self.exp)
        if self.exp.__class__ is Term and (self.exp.coef != 1 or self.exp.exp != 1):
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

    def __repr__(self) -> str:
        return str(self)

    @cache
    def __contains__(self, value: Variable) -> bool:
        return value in str(self)

    @cache
    def __add__(a, b: Term) -> Term:
        if a.like(b):
            return a.value.add(Proxy(b), a)
        return Polynomial.resolve(Proxy(b), a)

    @cache
    def __sub__(a, b: Term) -> Term:
        return a + -b

    @cache
    def __mul__(a, b: Term) -> Term:
        if a.value.__class__ is Number and (v := a.split_const_from_exp()):
            return b * v * Term(a.coef, a.value, a.exp - Term())
        if b.value.__class__ is Number and (v := b.split_const_from_exp()):
            return a * v * Term(b.coef, b.value, b.exp - Term())
        return a.value.mul(Proxy(b), a) or Product.resolve(a, b)

    @cache
    def __truediv__(a, b: Term) -> Term:
        if a.value.__class__ is Polynomial:
            a, b = Term.rationalize(a, b)
            gcd_a = gcd_b = Term()

            if a.value.__class__ is Polynomial and a.exp == 1:
                gcd_a = a.value.gcd()
                if gcd_a.value != 1:
                    a = Polynomial.long_division(a, gcd_a)
                if b.value.__class__ is Polynomial:
                    if b.exp == 1 and (gcd_b := b.value.gcd().canonical()).value != 1:
                        b = Polynomial.long_division(b, gcd_b)
                else:
                    gcd_b = Term.gcd(gcd_a, b).canonical()
                    if gcd_b.value != 1:
                        b /= gcd_b
            fac = gcd_a / gcd_b
            if not fac.remainder.value:
                return Polynomial.long_division(a * fac, b)
            # First step: Cancels common terms, returns a single fraction
            res = Polynomial.long_division(a, b, 0)
            # Last step: puts factors back and divides
            return Polynomial.long_division(
                res.numerator * fac.numerator, res.denominator * fac.denominator
            )

        return a * b.inv

    @cache
    def __pow__(a, b: Term) -> Term:
        if b.value == 0:
            return Term()
        if a.value == 1:
            return a
        return a.value.pow(Proxy(b), a) or (
            Term(a.coef) ** b * Term(value=a.value, exp=Term(value=a.exp) * b)
        )

    def __pos__(self) -> Term:
        return self

    @cache
    def __neg__(self) -> Term:
        return self * Term(Number(-1))

    @cache
    def __abs__(self) -> Term:
        """
        Gets the absolute of a term.
        It assumes in the cases of unkowns, get the absolute value of their coefficients.
        This method is not meant to be used outside the internal backend.
        """
        if not self.value.__class__ is Number or self.exp != 1:
            return Term(abs(self.coef), self.value, self.exp)
        return Term(value=abs(self.value), exp=self.exp)

    @lru_cache
    def scale(a, b: Number) -> Term:
        """Scale a by constant b"""
        if a.value.__class__ is Number and a.exp == 1:
            return Term(a.value * b)
        return Term(a.coef * b, a.value, a.exp)

    @lru_cache
    def canonical(self) -> Term:
        """
        A minimalist version of the input that has 1 as the coefficient.
        This can be used to group like terms for Polynomials
        """
        if self.value.__class__ is Number and self.exp == 1:
            return Term()
        return Term(value=self.value, exp=self.exp)

    @lru_cache
    def gcd_coefs(self) -> tuple[int]:
        """
        Get all the constants associated with a term (coefficient or value).
        Meant for use for finding the gcd of the constants in term
        """
        coef = self.to_const()
        was_imag = 0
        res = []
        # Imaginary numbers get split into their individual components
        # Same as would be with Polynomials
        if coef.numerator.imag:
            res.append(int(coef.numerator.real))
            res.append(int(coef.numerator.imag))
            was_imag = 1

        # Get the constants inside a polynomial with a constant exponent
        if self.value.__class__ is Polynomial and abs(self.exp) == 1:
            for i in self.value:
                res.extend(i.gcd_coefs())
            if self.exp == 1:
                return tuple(res)
        if not was_imag:
            res.append(coef.numerator)
        return tuple(res)

    @cached_property
    def numerator(self) -> Term:
        """Get the numerator of a term"""
        if self.value.__class__ is Product:
            return self.value.numerator * Term(Number(self.coef.numerator))
        if self.value.__class__ is Number and self.exp == 1:
            return Term(Number(self.value.numerator))
        if self.exp_const() > 0:
            return Term(Number(self.to_const().numerator), self.value, self.exp)
        return Term(Number(self.to_const().numerator))

    @cached_property
    def denominator(self) -> Term:
        """Get the denominator of a term"""
        if self.value.__class__ is Product:
            return self.value.denominator * Term(Number(self.coef.denominator))
        if self.value.__class__ is Number and self.exp == 1:
            return Term(Number(self.value.denominator))
        if self.exp_const() < 0:
            return Term(Number(self.coef.denominator), self.value, -self.exp)
        return Term(Number(self.coef.denominator))

    @cached_property
    def inv(self) -> Term:
        """The inverse of a term (x^-1)"""
        return self ** -Term()

    @cached_property
    def remainder(self) -> Term:
        """Get the term with a non-constant denominator"""
        if not self.denominator.value.__class__ is Number or self.denominator.exp != 1:
            return self
        if self.exp != 1:
            return Term(Number(0))
        if self.value.__class__ is Polynomial:
            for i in self.value:
                if (r := i.remainder).value:
                    return r
        return Term(Number(0))

    def exp_const(self) -> Number:
        """Get the constant in a term's exponent"""
        return self.exp if self.exp.__class__ is Number else self.exp.coef

    def get_exp(self, value: Variable) -> Number | Term:
        """
        Get the exponent of the given variable.
        Mostly meant to help with solving by factorization
        """
        if self.value == value:
            return self.exp
        if isinstance(self.value, Collection) and self.exp == 1:
            for t in self.value:
                if v := t.get_exp(value):
                    return v
        return Number()

    def to_const(self) -> Number:
        """
        Get the constant value associated with a term.
        For a number, itself, and for an unkown, the coefficient
        """
        if self.value.__class__ is Number and self.exp == 1:
            return self.value
        return self.coef

    def split_const_from_exp(self) -> Term | None:
        """
        If a term is in the form x^(y + n), where n is a constant,
        return x^n
        """
        if self.exp.__class__ is Number:
            return
        if self.exp.value.__class__ is Polynomial and self.exp.exp == 1:
            for i in self.exp.value:
                if i.value == 1:
                    return Term(value=self.value)

    @cache
    def like(self, b: Any, exp=1) -> bool:
        """Determine whether a term is like another"""
        if not b.__class__ is Term:
            return False
        # Assumes in the case of multiplications, values with the same base are like terms
        if not exp and self.value == b.value:
            return True
        # Check list to declare two terms like
        if (
            not self.exp.like(b.exp)
            or not b.value.__class__ is self.value.__class__
            or (exp)
            and (
                self.exp != b.exp
                or b.value.__class__ is Number
                and (self.exp != 1 and self.value != b.value)
            )
        ):
            return False
        if not b.value.__class__ is Number:
            return self.value == b.value
        return True

    @staticmethod
    @lru_cache
    def rationalize(a: Term, b: Term) -> tuple[Term]:
        """Given a : b, express a and b such that neither a nor b contain fractions"""
        # Removing symbolic fractions
        for i in (a.remainder.denominator, b.remainder.denominator):
            if i.value != 1:
                a *= i
                b *= i
        den = a.denominator * b.denominator
        a *= den
        b *= den
        # Fractions inside a polynomial
        if a.exp == 1 and a.value.__class__ is Polynomial:
            for i in a.value:
                if i.denominator.value != 1:
                    a *= i.denominator
                    b *= i.denominator
        if p := b.exp == 1 and b.value.__class__ is Polynomial:
            for i in b.value:
                if i.denominator.value != 1:
                    a *= i.denominator
                    b *= i.denominator

        # Factoring by gcd
        if (gcd := math.gcd(*a.gcd_coefs(), *b.gcd_coefs())) != 1:
            gcd = Term(Number(gcd) ** -1)
            a *= gcd
            b *= gcd

        # Make the denominator or leading denominator positive for consistency
        if max(b.gcd_coefs()) < 0 or (p and b.value.leading.coef < 0):
            a = -a
            b = -b
        return a, b

    @staticmethod
    @lru_cache
    def gcd(a: Term, b: Term) -> Term:
        """Greatest Common Divisor of a & b"""
        if lexicographic_weight(b, 0) > lexicographic_weight(a, 0):
            a, b = b, a
        if b.value.__class__ is Number and not a.value.__class__ is Number:
            return Term()
        # To prevent infinite recursion, call long division when applicable
        if a.value.__class__ is Polynomial:
            div = lambda a, b: Polynomial.long_division(a, b, 0)
        else:
            div = lambda a, b: a / b
        b2 = b
        while b.value != 1:
            if (d := div(a, b).remainder.denominator) == b:
                return Term()
            a, b = b, d
        if a.value != 1 and a != b2:
            a = div(b2, a)
        return a

    @staticmethod
    @lru_cache
    def lcm(a: Term, b: Term) -> Term:
        """Lowest Common Multiple of a & b"""
        if a == b:
            return a
        return (a * b) / Term.gcd(a, b)
