from .bases import Unknown, Base
from utils import *


class Variable(Unknown, str, Base):
    """An unknown in an experssion"""

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
        b = b.value
        if a.like(b, 0):
            if type(a.exp) is not type(b.exp):
                exp = type(a)(value=a.exp) + type(a)(value=b.exp)
            else:
                exp = a.exp + b.exp
            return type(a)(a.coef * b.coef, a.value, exp)

    @mul.register(number)
    def _(b, a):
        if b.value.exp == 1:
            return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial | product)
    def _(b, a):
        return b.value.value.mul(Proxy(a), b.value)

    @dispatch
    def pow(b, a):
        # Algebra object has a good enough default fallback for Variable exponentiation
        pass

    pow.register(polynomial)(Base.poly_pow)
