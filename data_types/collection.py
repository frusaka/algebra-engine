from .bases import *
from utils import *


class Collection(Unknown, set, Base):
    def __hash__(self):
        return hash((type(self), tuple(standard_form(self))))

    @dispatch
    def pow(b, a):
        pass

    @pow.register(number)
    def scalar_pow(b, a):
        b = b.value
        if b.exp != 1 or a.exp != 1:
            if b.coef != 1:
                return (a ** type(a)(b.coef)) ** type(a)(b.value, exp=b.exp)
            return
        b = b.value
        if b.imag:
            if isinstance(exp, type(a)):
                exp = a.exp * type(a)(b.value)
            else:
                exp = a.exp * b.value
            return type(a)(a.coef**b.value, a.value, exp)
        b = b.real
        res = a
        for _ in range(abs(b.numerator) - 1):
            res *= a
        exp = Fraction(1, b.denominator)
        if b < 0:
            exp = -exp
        return type(a)(res.coef**exp, res.value, res.exp * exp)

    pow.register(polynomial)(Base.poly_pow)
