from fractions import Fraction
from utils import *


class Base:
    def like(self, other):
        if type(self) is not type(other):
            return 0
        if isinstance(self, Number):
            return 1
        return self == other


class Unknown:
    def __eq__(self, value):
        return super().__eq__(value) and type(value) is type(self)

    def __gt__(self, value):
        return False

    def __lt__(self, value):
        return False

    def __ge__(self, value):
        return self == value

    def __le__(self, value):
        return self == value


class Variable(Unknown, str, Base):
    def __hash__(self):
        return str.__hash__(self)

    @dispatch
    def add(b, a):
        return type(a)(a.coef + b.value.coef, a.value, a.exp)

    @dispatch
    def mul(b, a):
        pass

    @mul.register(variable)
    def _(b, a):
        if a.like(b.value, 0):
            return type(a)(a.coef * b.value.coef, a.value, a.exp + b.value.exp)

    @mul.register(number)
    def _(b, a):
        if b.value.exp == 1:
            return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial | product)
    def _(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @dispatch
    def pow(b, a):
        pass

    @pow.register(number)
    def _(b, a):
        return Collection.scalar_pow(b, a)


class Number(Fraction, Base):
    @dispatch
    def add(b, a):
        pass

    @add.register(number)
    def _(b, a):
        b = b.value
        if a.exp == b.exp == 1:
            return type(a)(value=a.value + b.value)
        return type(a)(a.coef + b.coef, a.value, a.exp)

    @dispatch
    def mul(b, a):
        pass

    @mul.register(number)
    def _(b, a):
        b = b.value
        if a.like(b, 0):
            return type(a)(a.coef * b.coef, a.value * b.value, exp=a.exp)
        if a.exp == 1:
            return type(a)(a.value * b.coef, b.value, b.exp)
        if b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

    @mul.register(variable | polynomial | product)
    def _(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @dispatch
    def pow(b, a):
        pass

    @pow.register(number)
    def _(b, a):
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
        if (res := super().__pow__(other)).imag:
            raise ValueError("Complex result")
        return Number(res)

    def __abs__(self):
        return Number(super().__abs__())

    def __neg__(self):
        return Number(super().__neg__())

    def __pos__(self):
        return self


class Collection(Unknown, set, Base):
    def __hash__(self):
        return hash((type(self), tuple(standard_form(self))))

    @dispatch
    def pow(b, a):
        pass

    @pow.register(number)
    def scalar_pow(b, a):
        if not isinstance(a.exp, Number):
            return
        b = b.value
        res = a
        for _ in range(abs(b.value.numerator) - 1):
            res *= a
        exp = Number(1, b.value.denominator)
        if b.value < 0:
            exp = -exp
        return type(a)(res.coef**exp, res.value, res.exp * exp)
