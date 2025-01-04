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


class Number(Base):
    def __init__(self, real=0, imag=0):
        self.real = Fraction(real)
        self.imag = Fraction(imag)

    def __hash__(self):
        return hash((Number, self.real, self.imag))

    def __eq__(self, value):
        return self.real == value.real and self.imag == value.imag

    def __ne__(self, value):
        return not self == value

    def __gt__(self, value):
        if self.imag or value.imag:
            return False
        return self.real > value.real

    def __ge__(self, value):
        if self.imag or value.imag:
            return False
        return self.real >= value.real

    def __lt__(self, value):
        if self.imag or value.imag:
            return False
        return self.real < value.real

    def __le__(self, value):
        if self.imag or value.imag:
            return False
        return self.real <= value.real

    @property
    def numerator(self):
        if not self.imag:
            return self.real.numerator
        return self

    @property
    def denominator(self):
        if not self.imag:
            return self.real.denominator
        return 1

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
            return type(a)(a.coef * b.coef, a.value * b.value, a.exp)
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
        if a.exp == 1:
            return type(a)(a.coef, a.value**b.value.value, a.exp)
        return Collection.scalar_pow(b, a)

    def __str__(self):
        if self.imag:
            i = print_frac(self.imag)
            if i == "1":
                i = i[1:]
            i += "i"
            if self.real:
                op = "+"
                if i.startswith("-"):
                    op = "-"
                    i = i[1:]
                return op.join((print_frac(self.real), i))
            return i
        return print_frac(self.real)

    def __add__(self, other):
        return Number(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return Number(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        real = self.real * other.real - self.imag * other.imag
        imag = self.real * other.imag + self.imag * other.real
        return Number(real, imag)

    def __truediv__(self, other):
        return self * other ** Number(-1)

    def __pow__(self, other):
        if self.imag:
            if other.real.denominator != 1:
                raise NotImplementedError("Cannot root complex base")
            if other.real.numerator < 0:
                raise NotImplementedError("Cannot inverse complex number")
        else:
            res = self.real**other.real
            return Number(res.real, res.imag)
        res = self
        for _ in range(other.real.numerator - 1):
            res *= self
        return res

    def __abs__(self):
        return Number((self.real**2 + self.imag**2) ** 0.5)

    def __neg__(self):
        return Number(-self.real, -self.imag)

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
        b = b.value.value.real
        res = a
        for _ in range(abs(b.numerator) - 1):
            res *= a
        exp = Fraction(1, b.denominator)
        if b < 0:
            exp = -exp
        return type(a)(res.coef**exp, res.value, res.exp * exp)
