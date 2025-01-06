from .collection import Collection
from .number import Number
from .polynomial import Polynomial
from utils import *


class Product(Collection):
    def __str__(self):
        num, den = [], []
        for algebraobject in reversed(standard_form(self)):
            exp = (
                algebraobject.exp
                if isinstance(algebraobject.exp, Number)
                else algebraobject.exp.coef
            )
            if exp < 0:
                den.append(
                    str(
                        type(algebraobject)(
                            value=algebraobject.value, exp=abs(algebraobject.exp)
                        )
                    )
                )
            else:
                num.append(str(algebraobject))
        a, b = "•".join(num), "•".join(den)
        if len(num) > 1:
            a = a.join("()")
        if len(den) > 1:
            b = b.join("()")
        if not num:
            return f"1/{b}".join("()")
        if den:
            return f"{a}/{b}".join("()")
        return a

    @dispatch
    def add(b, a):
        if a.like(b.value):
            return type(a)(a.coef + b.value.coef, a.value)

    @dispatch
    def mul(b, a):
        pass

    @mul.register(product | variable)
    def _(b, a):
        b = b.value
        c = a.coef * b.coef
        res = Product.simplify(a.value, type(a)(value=b.value, exp=b.exp))
        if res:
            if len(res) == 1:
                res = res.pop()
                return type(a)(c, res.value, res.exp)
            return type(a)(c, Product(res))
        return type(a)(value=c)

    @mul.register(number)
    def _(b, a):
        if b.value.exp != 1:
            rem = Product.simplify(a.value, b.value)
            if not rem:
                return type(a)(value=a.coef)
            return type(a)(a.coef, Product(rem))
        return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial)
    def _(b, a):
        return Polynomial.mul(Proxy(a), b.value)

    @dispatch
    def pow(b, a):
        res = type(a)()
        for i in a.value:
            res *= i**b.value
        return res * type(a)(value=a.coef) ** b.value

    @staticmethod
    def resolve(a, b):
        c = a.coef * b.coef
        a = type(a)(value=a.value, exp=a.exp)
        b = type(a)(value=b.value, exp=b.exp)
        return type(a)(c, Product([a, b]))

    @staticmethod
    def simplify(a, b):
        algebraobjects = a.copy()
        rem = (b.value if isinstance(b.value, Product) else {b}).copy()
        for a in tuple(algebraobjects):
            for b in tuple(rem):
                if not algebraobjects:
                    break
                if a.like(b, 0):
                    algebraobjects.remove(a)
                    rem.remove(b)
                    a *= b
                    if a.value != 1:
                        algebraobjects.add(a)
        return algebraobjects.union(rem)
