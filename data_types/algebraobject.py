from __future__ import annotations
from dataclasses import dataclass
from functools import cache, cached_property
import math
from typing import Tuple
from .bases import Base
from .number import Number
from .variable import Variable
from .collection import Collection
from .product import Product
from .polynomial import Polynomial
from utils import Proxy, print_coef


@dataclass(frozen=True, init=False, order=True)
class AlgebraObject:
    coef: Number
    value: Base[Number, Variable, Product, Polynomial]
    exp: Number | AlgebraObject

    def __new__(cls, coef=Number(1), value=Number(1), exp=Number(1)):
        obj = super().__new__(cls)
        if isinstance(value, AlgebraObject):
            object.__setattr__(obj, "coef", value.coef)
            object.__setattr__(obj, "value", value.value)
            object.__setattr__(obj, "exp", value.exp)
            return obj
        # Cases when operations with exponents simplify to a constant
        if (
            isinstance(exp, AlgebraObject)
            and isinstance(exp.value, Number)
            and exp.exp == 1
        ):
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
        """String representation of a term"""
        # Numbers with symbolic exponents
        if isinstance(self.value, Number) and self.exp != 1:
            if self.coef != 1:
                return "{0}{1}".format(
                    print_coef(self.coef), AlgebraObject(value=self.value, exp=self.exp)
                )
            return (
                str(AlgebraObject(value="$", exp=self.exp))
                .join("()")
                .replace("$", str(self.value))
            )
        # Negative exponets: ax^-n -> a/x^n
        if self.exp_const() < 0:
            return "{0}/{1}".format(
                self.coef.numerator,
                AlgebraObject(Number(self.coef.denominator), self.value, -self.exp),
            )
        if "/" in str(self.coef):
            return "{0}/{1}".format(self.numerator, self.denominator)
        res = print_coef(self.coef)
        # Cases when a Polynomial or Product has no symbolic numerator
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
                val = AlgebraObject(value=self.value, exp=self.exp)
                if self.coef == -1:
                    return "-{0}".format(val)
                return "{0}({1})".format(print_coef(self.coef), val)
            if exp.numerator != 1:
                res = "{0}^{1}".format(res, exp.numerator)
            return "{0}√{1}".format(exp.denominator, res)

        # Symbolic exponent representation
        exp = str(self.exp)
        if isinstance(self.exp, AlgebraObject) and (
            self.exp.coef != 1 or self.exp.exp != 1
        ):
            exp = exp.join("()")
        return "{0}^{1}".format(res, exp)

    @cache
    def __contains__(self, value: Variable) -> bool:
        """
        Check whether a term contains the given variable, whether by values or exponent.
        """
        if isinstance(self.value, Collection):
            return any(value in t for t in self.value)
        if (
            self.value == value
            or isinstance(self.exp, AlgebraObject)
            and value in self.exp
        ):
            return True
        return False

    @cache
    def __add__(a, b: AlgebraObject) -> AlgebraObject:
        """Add b to a"""
        if a.like(b):
            return a.value.add(Proxy(b), a)
        return Polynomial.resolve(Proxy(b), a)

    @cache
    def __sub__(a, b: AlgebraObject) -> AlgebraObject:
        """Subtract b from a"""
        return a + -b

    @cache
    def __mul__(a, b: AlgebraObject) -> AlgebraObject:
        """Multiply a with b"""
        if v := a.split_const_from_exp():
            return b * v * AlgebraObject(a.coef, a.value, a.exp - AlgebraObject())
        if v := b.split_const_from_exp():
            return a * v * AlgebraObject(b.coef, b.value, b.exp - AlgebraObject())
        return a.value.mul(Proxy(b), a) or Product.resolve(a, b)

    @cache
    def __truediv__(a, b: AlgebraObject) -> AlgebraObject:
        """Divde a by b"""
        if isinstance(a.value, Polynomial):
            a, b = AlgebraObject.rationalize(a, b)
            return Polynomial.long_division(a, b)
        return a * b.inv

    @cache
    def __pow__(a, b: AlgebraObject) -> AlgebraObject:
        """Evaluate base a with an exponent of b"""
        if b.value == 0:
            return AlgebraObject()
        return a.value.pow(Proxy(b), a) or (
            AlgebraObject(a.coef) ** b
            * AlgebraObject(value=a.value, exp=AlgebraObject(value=a.exp) * b)
        )

    def __pos__(self) -> AlgebraObject:
        """Positive x, does nothing"""
        return self

    @cache
    def __neg__(self) -> AlgebraObject:
        """Negation"""
        return self * AlgebraObject(value=Number(-1))

    @cache
    def __abs__(self) -> AlgebraObject:
        """
        Gets the absolute of a term.
        It assumes in the cases of unkowns, get the absolute value of their coefficients.
        This method is not meant to be used outside the internal backend.
        """
        if not isinstance(self.value, Number) or self.exp != 1:
            return AlgebraObject(abs(self.coef), self.value, self.exp)
        return AlgebraObject(value=abs(self.value), exp=self.exp)

    @cache
    def scale(a, b: Number) -> AlgebraObject:
        """Scale a by constant b"""
        if isinstance(a.value, Number) and a.exp == 1:
            return AlgebraObject(a.value * b)
        return AlgebraObject(a.coef * b, a.value, a.exp)

    @cache
    def canonical(self) -> AlgebraObject:
        """
        A minimalist version of the input that does not have magnitude data.
        This can be used to group like terms for Polynomials
        """
        if isinstance(self.value, Number) and self.exp == 1:
            return AlgebraObject()
        return AlgebraObject(value=self.value, exp=self.exp)

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
    def numerator(self) -> AlgebraObject:
        """Get the numerator of a term"""
        if isinstance(self.value, Product):
            return self.value.numerator * AlgebraObject(Number(self.coef.numerator))
        if isinstance(self.value, Number) and self.exp == 1:
            return AlgebraObject(Number(self.value.numerator))
        if self.exp_const() > 0:
            return AlgebraObject(
                Number(self.to_const().numerator), self.value, self.exp
            )
        return AlgebraObject(Number(self.to_const().numerator))

    @cached_property
    def denominator(self) -> AlgebraObject:
        """Get the denominator of a term"""
        if isinstance(self.value, Product):
            return self.value.denominator * AlgebraObject(Number(self.coef.denominator))
        if isinstance(self.value, Number) and self.exp == 1:
            return AlgebraObject(Number(self.value.denominator))
        if self.exp_const() < 0:
            return AlgebraObject(
                Number(self.coef.denominator), self.value, self.exp
            ).inv
        return AlgebraObject(Number(self.to_const().denominator))

    @cached_property
    def inv(self) -> AlgebraObject:
        """Get the inverse"""
        return self ** -AlgebraObject()

    @cached_property
    def remainder(self):
        """The term that has non constant denominator"""
        if not isinstance(self.denominator.value, Number) or self.denominator.exp != 1:
            return self.numerator
        if self.exp != 1:
            return AlgebraObject(Number(0))
        if isinstance(self.value, Polynomial):
            for i in self.value:
                if (r := i.remainder).value:
                    return r
        return AlgebraObject(Number(0))

    def exp_const(self) -> Number:
        """Get the constant in a terms exponent"""
        return self.exp if isinstance(self.exp, Number) else self.exp.coef

    def to_const(self) -> Number:
        """
        Get the constant value associated with a term.
        For a number, itself, and for an unkown, the coefficient
        """
        if isinstance(self.value, Number) and self.exp == 1:
            return self.value
        return self.coef

    def split_const_from_exp(self) -> AlgebraObject | None:
        """
        If a term is in the form x^(y + n), where n is a constant,
        return x^n
        """
        if isinstance(self.exp, Number):
            return
        if isinstance(self.exp.value, Polynomial) and self.exp.exp == 1:
            for i in self.exp.value:
                if i.value == 1:
                    return AlgebraObject(value=self.value)

    @cache
    def like(self, b, exp=1) -> bool:
        """Determine whether a term is like another"""
        if not isinstance(b, AlgebraObject):
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
    def rationalize(a: AlgebraObject, b: AlgebraObject):
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
        gcd = math.gcd(*a.gcd_coefs(), *b.gcd_coefs())
        if gcd != 1:
            gcd = AlgebraObject(Number(gcd) ** -1)
            a *= gcd
            b *= gcd
        # Make the denominator or leading denominator positive for consistency
        if max(b.gcd_coefs()) < 0 or (p and b.value.leading.coef < 0):
            a = -a
            b = -b
        return a, b

    @staticmethod
    @cache
    def gcd(a: AlgebraObject, b: AlgebraObject):
        """Greatest Common Divisor of a & b"""

        def gcd(a, b):
            while b.value != 0:
                r = (a / b).remainder
                if r == a:
                    return AlgebraObject()
                a, b = b, r
            return a

        if (val := gcd(a, b)).value == 1:
            return gcd(b, a)
        return val

    @staticmethod
    @cache
    def lcm(a: AlgebraObject, b: AlgebraObject):
        """Lowest Common Multiple of a & b"""
        return (a * b) / AlgebraObject.gcd(a, b)
