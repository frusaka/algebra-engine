from .bases import Base, Fraction
from utils import *


class Number(Base):
    def __init__(self, real=0, imag=0):  # Experimental
        real = Fraction(real)
        imag = Fraction(imag)
        den = (real + imag).denominator
        if imag:
            self.numerator = complex(
                (den / real.denominator) * real.numerator,
                (den / imag.denominator) * imag.numerator,
            )
        else:
            self.numerator = real.numerator
        self.denominator = den

    def __init__(self, real=0, imag=0):
        self.real = Fraction(real)
        self.imag = Fraction(imag)

    def __hash__(self):
        return hash((Number, self.real, self.imag))

    def __bool__(self):
        return bool(self.real) or bool(self.imag)

    def __str__(self):
        if self.imag:
            i = print_frac(self.imag)
            if i == "1":
                i = ""
            elif i == "-1":
                i = "-"
            if "/" in i:
                i = "/".join(
                    (str(Number(imag=self.imag.numerator)), str(self.imag.denominator))
                )
            else:
                i += "i"
            if self.real:
                op = "+"
                if i.startswith("-"):
                    op = "-"
                    i = i[1:]
                return op.join((print_frac(self.real), i))
            return i
        return print_frac(self.real)

    def __repr__(self):
        return "Number(real={0}, imag={1})".format(repr(self.real), repr(self.imag))

    def __add__(self, other):
        return Number(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return Number(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        real = self.real * other.real - self.imag * other.imag
        imag = self.real * other.imag + self.imag * other.real
        return Number(real, imag)

    def __truediv__(self, other):
        a, b = self.real, self.imag
        c, d = other.real, other.imag
        denom = c**2 + d**2
        real = (a * c + b * d) / denom
        imag = (b * c - a * d) / denom
        return Number(real, imag)

    def __pow__(self, other):
        # Trying to keep the precision of the Fraction class
        if other == 1:
            return self
        if not other.imag and other.real.numerator < 0:
            return Number(1) / self ** abs(other.real)
        res = complex(self.real, self.imag) ** complex(other.real, other.imag)
        return Number(res.real, res.imag)

    def __abs__(self):
        return Number((self.real**2 + self.imag**2) ** 0.5)

    def __neg__(self):
        return Number(-self.real, -self.imag)

    def __pos__(self):
        return self

    def __eq__(self, value):
        if not hasattr(value, "imag"):
            return False
        return self.real == value.real and self.imag == value.imag

    def __ne__(self, value):
        return not self == value

    def __gt__(self, value):
        if not hasattr(value, "imag"):
            return False
        if self.imag == value.imag:
            return self.real > value.real
        if self.real == value.real:
            return self.imag > value.imag
        return False

    def __ge__(self, value):
        if not hasattr(value, "imag"):
            return False
        if self.imag == value.imag:
            return self.real >= value.real
        if self.real == value.real:
            return self.imag >= value.imag
        return False

    def __lt__(self, value):
        if not hasattr(value, "imag"):
            return False
        if self.imag == value.imag:
            return self.real < value.real
        if self.real == value.real:
            return self.imag < value.imag
        return False

    def __le__(self, value):
        if not hasattr(value, "imag"):
            return False
        if self.imag == value.imag:
            return self.real <= value.real
        if self.real == value.real:
            return self.imag <= value.imag
        return False

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
        return b.value.value.mul(Proxy(a), b.value)

    @mul.register(number)
    def _(b, a):
        b = b.value
        if a.like(b, 0):
            # Can be like term with different exponents (3^x * 3^y)
            if a.exp == b.exp:
                return type(a)(a.coef * b.coef, a.value * b.value, a.exp)
            return type(a)(a.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp))
        if a.exp == 1:
            return type(a)(a.value * b.coef, b.value, b.exp)
        if b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

    @staticmethod
    def resolve_pow(a, b):
        # NOTE: a^(nm) = (a^n)^m only if m is a real integer
        res = type(a)(a.coef, a.value) ** type(a)(b.tovalue())
        return type(a)(
            res.coef, res.value, type(a)(value=a.exp) * (b / type(a)(b.tovalue()))
        )

    @dispatch
    def pow(b, a):
        return Number.resolve_pow(a, b.value)

    @pow.register(number)
    def _(b, a):
        if a.exp == b.value.exp == 1:
            return type(a)(a.coef, a.value**b.value.value, a.exp)
        return Number.resolve_pow(a, b.value)

    pow.register(polynomial)(Base.poly_pow)
