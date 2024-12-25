from functools import singledispatchmethod
from fractions import Fraction
from utils import *


class Base:
    def like(self, other):
        if type(self) != type(other):
            return 0
        if isinstance(self, Number):
            return 1
        return self == other

    @staticmethod
    def add(a, b):
        return a.value.add(Proxy(b), a)

    @staticmethod
    def mul(a, b):
        return a.value.mul(Proxy(b), a)

    @staticmethod
    def pow(a, b):
        return a.value.pow(Proxy(b), a)


class Variable(str, Base):
    @singledispatchmethod
    @staticmethod
    def add(b, a):
        pass

    @add.register(variable)
    @staticmethod
    def _(b, a):
        if a.like(b.value):
            return type(a)(a.coef + b.value.coef, a.value, a.exp)

    @singledispatchmethod
    @staticmethod
    def mul(b, a):
        pass

    @mul.register(variable)
    @staticmethod
    def _(b, a):
        if a.like(b.value, 0):
            return type(a)(a.coef * b.value.coef, a.value, a.exp + b.value.exp)

    @mul.register(number)
    @staticmethod
    def _(b, a):
        if b.value.exp == 1:
            return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial | factor)
    @staticmethod
    def _(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @singledispatchmethod
    @staticmethod
    def pow(b, a):
        pass

    @pow.register(number)
    @staticmethod
    def _(b, a):
        return Collection.scalar_pow(b, a)


class Number(Fraction, Base):
    @singledispatchmethod
    @staticmethod
    def add(b, a):
        pass

    @add.register(number)
    @staticmethod
    def _(b, a):
        if a.like(b.value):
            return type(a)(value=a.value + b.value.value)

    @singledispatchmethod
    @staticmethod
    def mul(b, a):
        pass

    @mul.register(number)
    @staticmethod
    def _(b, a):
        if a.like(b.value, 0):
            return type(a)(value=a.value * b.value.value, exp=a.exp)

    @mul.register(variable | polynomial | factor)
    @staticmethod
    def _(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @singledispatchmethod
    @staticmethod
    def pow(b, a):
        pass

    @pow.register(number)
    @staticmethod
    def _(b, a):
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
    @staticmethod
    def pow(b, a):
        pass

    @pow.register(number)
    @staticmethod
    def scalar_pow(b, a):
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
