from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from functools import cache, cached_property
import math
from .bases import Atomic
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
    value: Atomic[Number, Variable, Product, Polynomial]
    exp: Number | Term

    def __new__(cls, coef=Number(1), value=Number(1), exp=Number(1)) -> Term:
        obj = super().__new__(cls)
        if isinstance(value, Term):
            object.__setattr__(obj, "coef", value.coef)
            object.__setattr__(obj, "value", value.value)
            object.__setattr__(obj, "exp", value.exp)
            return obj
        # Cases when operations with exponents simplify to a constant
        if isinstance(exp, Term) and isinstance(exp.value, Number) and exp.exp == 1:
            exp = exp.value
        # Aplying basic known algebraic rules to validate the term
        if coef == 0:
            value = Number(0)
            coef = exp = Number(1)
        elif coef != 1 and value == 1:
            value, coef = coef, value
            exp = coef
        elif exp == 0:
            value = coef
            exp = coef = Number(1)
        # 1^n = 1 for any value of n
        elif value == 1:
            exp = value
        object.__setattr__(obj, "coef", coef)
        object.__setattr__(obj, "value", value)
        object.__setattr__(obj, "exp", exp)
        return obj

    def __str__(self) -> str:
        if (
            "/" in str(self.coef)
            or isinstance(self.value, Product)
            and self.coef.denominator != 1
        ):
            return "{0}/{1}".format(self.numerator, self.denominator)
        # Numbers with symbolic exponents
        if isinstance(self.value, Number) and self.exp != 1:
            return "{0}{1}".format(
                print_coef(self.coef),
                str(Term(value="$", exp=self.exp))
                .join("()")
                .replace("$", str(self.value)),
            )
        # Negative exponets: ax^-n -> a/x^n
        if self.exp_const() < 0:
            return "{0}/{1}".format(self.numerator, self.denominator)
        res = print_coef(self.coef)
        # Cases when a Polynomial or Product has no variable numerator
        # Instead of 3(1/(abc)), prints 3/(abc)
        if isinstance(self.value, Collection) and isinstance(
            self.numerator.value, Number
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
        if isinstance(self.exp, Term) and (self.exp.coef != 1 or self.exp.exp != 1):
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

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
        if v := a.split_const_from_exp():
            return b * v * Term(a.coef, a.value, a.exp - Term())
        if v := b.split_const_from_exp():
            return a * v * Term(b.coef, b.value, b.exp - Term())
        return a.value.mul(Proxy(b), a) or Product.resolve(a, b)

    @cache
    def __truediv__(a, b: Term) -> Term:
        if isinstance(a.value, Polynomial):
            a, b = Term.rationalize(a, b)
            gcd_a, gcd_b = (Term(),) * 2
            # Factorize the Polynomial
            if (
                isinstance(a.value, Polynomial)
                and isinstance(b.value, Polynomial)
                and a.exp == b.exp == 1
            ):
                gcd_a = gcd_b = Term()
                gcd_a = a.value.gcd()
                gcd_b = b.value.gcd()
                if gcd_a.value != 1:
                    a = Polynomial.long_division(a, gcd_a)
                if gcd_b.value != 1:
                    b = Polynomial.long_division(b, gcd_b)
            # Divide the simplified Polynomial
            res = Polynomial.long_division(a, b)
            # Combine with the gcd
            # Not fully sufficient:
            #   e.g, ((2x^4 - 8x^2)/(x^4 - 10x^3)) * ((x + 7)/(4x^2 + 36x + 56))
            #   Engine result -> (x^2 - 4)/(2x^3 - 16x^2 - 40x)
            #   Simplify further:
            #       (x+2)(x-2)/2x(x+2)(x-10)
            #       (x-2)/2x(x-10)
            frac = gcd_a / gcd_b
            a, b = Term.rationalize(res, Term())
            return Polynomial.long_division(a * frac.numerator, frac.denominator * b)
        return a * b.inv

    @cache
    def __pow__(a, b: Term) -> Term:
        if b.value == 0:
            return Term()
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
        if not isinstance(self.value, Number) or self.exp != 1:
            return Term(abs(self.coef), self.value, self.exp)
        if (
            isinstance(self.value, Polynomial)
            and abs(self.exp) == 1
            and next(iter(self.value.leading_options())).to_const() < 0
        ):
            return -self
        return Term(value=abs(self.value), exp=self.exp)

    @cache
    def scale(a, b: Number) -> Term:
        """Scale a by constant b"""
        if isinstance(a.value, Number) and a.exp == 1:
            return Term(a.value * b)
        return Term(a.coef * b, a.value, a.exp)

    @cache
    def canonical(self) -> Term:
        """
        A minimalist version of the input that has 1 as the coefficient.
        This can be used to group like terms for Polynomials
        """
        if isinstance(self.value, Number) and self.exp == 1:
            return Term()
        return Term(value=self.value, exp=self.exp)

    @cache
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
        if isinstance(self.value, Polynomial) and abs(self.exp) == 1:
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
        if isinstance(self.value, Product):
            return self.value.numerator * Term(Number(self.coef.numerator))
        if isinstance(self.value, Number) and self.exp == 1:
            return Term(Number(self.value.numerator))
        if self.exp_const() > 0:
            return Term(Number(self.to_const().numerator), self.value, self.exp)
        return Term(Number(self.to_const().numerator))

    @cached_property
    def denominator(self) -> Term:
        """Get the denominator of a term"""
        if isinstance(self.value, Product):
            return self.value.denominator * Term(Number(self.coef.denominator))
        if isinstance(self.value, Number) and self.exp == 1:
            return Term(Number(self.value.denominator))
        if self.exp_const() < 0:
            return Term(Number(self.coef.denominator), self.value, -self.exp)
        return Term(Number(self.coef.denominator))

    @cached_property
    def inv(self) -> Term:
        """The inverse of a term (x^-1)"""
        return self ** -Term()

    @cached_property
    def fractional(self) -> Term:
        """Get the term with a non-constant denominator"""
        if not isinstance(self.denominator.value, Number) or self.denominator.exp != 1:
            return self
        if self.exp != 1:
            return Term(Number(0))
        if isinstance(self.value, Polynomial):
            for i in self.value:
                if (r := i.fractional).value:
                    return r
        return Term(Number(0))

    @cached_property
    def remainder(self) -> Term:
        """The numerator of the term that has non constant denominator"""
        return self.fractional.numerator

    def exp_const(self) -> Number:
        """Get the constant in a terms exponent"""
        return self.exp if isinstance(self.exp, Number) else self.exp.coef

    @cache
    def get_exp(self, value: Variable) -> Number | Term:
        """
        Get the exponent of the given variable.
        Mostly meant to help with solving by factorization
        """
        if self.value == value:
            return self.exp
        if isinstance(self.value, Collection):
            for t in self.value:
                if v := t.get_exp(value):
                    return v
        if isinstance(self.exp, Term):
            return self.exp.get_exp(value)
        return Number()

    def to_const(self) -> Number:
        """
        Get the constant value associated with a term.
        For a number, itself, and for an unkown, the coefficient
        """
        if isinstance(self.value, Number) and self.exp == 1:
            return self.value
        return self.coef

    def split_const_from_exp(self) -> Term | None:
        """
        If a term is in the form x^(y + n), where n is a constant,
        return x^n
        """
        if isinstance(self.exp, Number):
            return
        if isinstance(self.exp.value, Polynomial) and self.exp.exp == 1:
            for i in self.exp.value:
                if i.value == 1:
                    return Term(value=self.value)

    @cache
    def like(self, b: Any, exp=1) -> bool:
        """Determine whether a term is like another"""
        if not isinstance(b, Term):
            return False
        # Assumes in the case of multiplications, values with the same base are like terms
        if not exp and self.value == b.value:
            return True
        # Check list to declare two terms like
        if (
            not self.exp.like(b.exp)
            or not isinstance(b.value, type(self.value))
            or (exp)
            and (
                self.exp != b.exp
                or isinstance(b.value, Number)
                and (self.exp != 1 and self.value != b.value)
            )
        ):
            return False
        if not isinstance(b.value, Number):
            return self.value == b.value
        return True

    @staticmethod
    @cache
    def rationalize(a: Term, b: Term) -> tuple[Term]:
        """Given a : b, express a and b such that neither a nor b contain fractions"""
        # Fractions at the top-level
        if a.denominator.value != 1:
            return a.rationalize(a * a.denominator, b * a.denominator)
        if b.denominator.value != 1:
            return a.rationalize(a * b.denominator, b * b.denominator)

        # Fractions inside a polynomial
        if a.exp == 1 and isinstance(a.value, Polynomial):
            for i in a.value:
                if i.denominator.value != 1:
                    return a.rationalize(a * i.denominator, b * i.denominator)
        if p := b.exp == 1 and isinstance(b.value, Polynomial):
            for i in b.value:
                if i.denominator.value != 1:
                    return a.rationalize(a * i.denominator, b * i.denominator)

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
    @cache
    def gcd(a: Term, b: Term) -> Term:
        """Greatest Common Divisor of a & b"""

        def gcd(a, b):
            while b.value != 0:
                r = (a / b).remainder
                if r == a:
                    return Term()
                a, b = b, r
            return a

        if lexicographic_weight(b, 0) > lexicographic_weight(a, 0):
            a, b = b, a
        return gcd(a, b)

    @staticmethod
    @cache
    def lcm(a: Term, b: Term) -> Term:
        """Lowest Common Multiple of a & b"""
        return (a * b) / Term.gcd(a, b)
