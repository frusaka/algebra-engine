from fractions import Fraction
import itertools
import operator
from utils import *
from functools import singledispatchmethod


class Base:
    def like(self, other):
        if type(self) != type(other):
            return 0
        if isinstance(self, Number):
            return 1
        return self == other

    @staticmethod
    def add(a: "Term", b: "Term"):  # type: ignore
        return a.value.add(Proxy(b, globals().get(type(b.value).__name__.lower())), a)

    @staticmethod
    def mul(a: "Term", b: "Term"):  # type: ignore
        return a.value.mul(Proxy(b, globals().get(type(b.value).__name__.lower())), a)

    @staticmethod
    def pow(a: "Term", b: "Term"):  # type: ignore
        return a.value.pow(Proxy(b, globals().get(type(b.value).__name__.lower())), a)


class Variable(str, Base):
    @singledispatchmethod
    def add(_, b, a):
        pass

    @add.register(variable)
    def _(_, b, a):
        return type(a)(a.coef + b.value.coef, a.value, a.exp)

    @singledispatchmethod
    def mul(_, b, a):
        pass

    @mul.register(variable)
    def _(_, b, a):
        if a.like(b.value, 0):
            return type(a)(a.coef * b.value.coef, a.value, a.exp + b.value.exp)

    @mul.register(number)
    def _(_, b, a):
        if b.value.exp != 1:
            return
        return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial | factor)
    def _(_, b, a):
        return b.value.value.mul(Proxy(a, variable), b.value)

    @singledispatchmethod
    def pow(_, b, a):
        pass

    @pow.register(number)
    def _(_, b, a):
        return Collection.scalar_pow(_, b, a)


class Number(Fraction, Base):
    @singledispatchmethod
    def add(_, b, a):
        pass

    @add.register(number)
    def _(_, b, a):
        return type(a)(value=a.value + b.value.value)

    @singledispatchmethod
    def mul(_, b, a):
        pass

    @mul.register(number)
    def _(_, b, a):
        if a.exp.like(b.value.exp):
            return type(a)(value=a.value * b.value.value, exp=a.exp)

    @mul.register(variable | polynomial | factor)
    def _(_, b, a):
        return b.value.value.mul(Proxy(a, number), b.value)

    @singledispatchmethod
    def pow(_, b, a):
        pass

    @pow.register(number)
    def _(_, b, a):
        if a.exp != 1:
            return
        return type(a)(value=a.value**b.value.value, exp=a.exp)

    def __str__(self):
        if any(not self.denominator % i for i in (2, 5)) and self.denominator % 3:
            return str(self.numerator / self.denominator)
        return super().__str__()

    def __add__(self, other):
        return Number(super().__add__(other))

    def __sub__(self, other):
        return Number(super().__sub__(other))

    def __mul__(self, other):
        return Number(super().__mul__(other))

    def __truediv__(self, other):
        return Number(super().__truediv__(other))

    def __pow__(self, other):
        return Number(super().__pow__(other))

    def __abs__(self):
        return Number(super().__abs__())

    def __neg__(self):
        return Number(super().__neg__())

    def __pos__(self):
        return self


class Collection(set, Base):
    def __hash__(self):
        return hash((type(self), tuple(self)))

    @singledispatchmethod
    def pow(_, b, a):
        pass

    @pow.register(number)
    def scalar_pow(_, b, a):
        b = b.value
        if b.value == 0:
            return type(a)()
        res = a
        for _ in range(abs(b.value.numerator) - 1):
            res *= a
        exp = Number(1, b.value.denominator)
        if b.value < 0:
            exp = -exp
        return type(a)(res.coef**exp, res.value, res.exp * exp)

    def flatten(self, term):
        if term.exp != 1 or not isinstance(term.value, type(self)):
            yield term
            return

        for i in term.value:
            yield from self.flatten(i)

    def like(self, other):
        return self == other
