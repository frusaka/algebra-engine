from .bases import *
from utils import *


class Collection(Unknown, set, Base):
    def __hash__(self):
        return hash((type(self), tuple(standard_form(self))))

    def flatten(self, algebraobject):
        if algebraobject.exp != 1 or not isinstance(algebraobject.value, type(self)):
            yield algebraobject
            return

        for i in algebraobject.value:
            yield from self.flatten(i)

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
        if b.numerator.imag:
            return type(a)(
                a.coef**b.value, a.value, type(a)(value=a.exp) * type(a)(b.value)
            )
        res = a
        for _ in range(abs(b.numerator) - 1):
            res *= a
        exp = Fraction(1, b.denominator)
        if b < 0:
            exp = -exp
        return type(a)(res.coef**exp, res.value, res.exp * exp)

    pow.register(polynomial)(Base.poly_pow)
