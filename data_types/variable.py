from .bases import Unknown, Base
from .collection import Collection

from utils import *


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
        b = b.value
        if a.coef == 1:
            return type(a)(value=a.value, exp=type(a)(value=a.exp) * b)
        c = b.coef
        b = type(a)(value=b.value, exp=b.exp)
        return type(a)(value=a.coef**c) ** b * type(a)(
            value=a.value, exp=b * type(a)(value=a.exp)
        )

    @pow.register(number)
    def _(b, a):
        return Collection.scalar_pow(b, a)

    @pow.register(polynomial)
    def _(b, a):
        return Base.poly_pow(b.value, a)
