from .collection import Collection
from utils import *
import itertools


class Product(Collection):
    def __new__(cls, algebraobjects):
        return super().__new__(
            cls,
            itertools.chain(
                *itertools.starmap(
                    cls.flatten, zip(algebraobjects, itertools.repeat(cls))
                )
            ),
        )

    def __str__(self):
        num, den = [], []
        for t in reversed(standard_form(self)):
            if t.exp_const() < 0:
                den.append(str(type(t)(value=t.value, exp=abs(t.exp))))
            else:
                num.append(str(t))
        a, b = "".join(num), "".join(den)
        if len(num) > 1 and den:
            a = a.join("()")
        if "(" in b and len(den) > 1:
            b = b.join("()")
        if not num:
            return f"1/{b}"
        if den:
            return f"{a}/{b}"
        return a

    @property
    def numerator(self):
        from .algebraobject import AlgebraObject

        res = AlgebraObject()
        for t in self:
            if t.exp_const() > 0:
                res *= t
        return res

    @property
    def denominator(self):
        from .algebraobject import AlgebraObject

        res = AlgebraObject()
        for t in self:
            if t.exp_const() < 0:
                res *= t ** -AlgebraObject()
        return res

    @staticmethod
    def _mul(b, a):
        c = a.coef * b.coef
        res = Product.simplify(a.value, type(a)(value=b.value, exp=b.exp))
        if res:
            if len(res) == 1:
                res = res.pop()
                return type(a)(c, res.value, res.exp)
            return type(a)(c, Product(res))
        return type(a)(value=c)

    @dispatch
    def add(b, a):
        if a.like(b.value):
            return type(a)(a.coef + b.value.coef, a.value)

    @dispatch
    def mul(b, a):
        return Product._mul(b.value, a)

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
        b = b.value
        if abs(b.exp) != 1:
            return Product._mul(b, a)
        return b.value.mul(Proxy(a), b)

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
        algebraobjects = set(a) if isinstance(a, Product) else {a}
        rem = set(b.value) if isinstance(b.value, Product) else {b}
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
