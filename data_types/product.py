from .bases import Collection, Number
from .polynomial import Polynomial
from utils import *


class Product(Collection):
    def __str__(self):
        num, den = [], []
        for term in reversed(standard_form(self)):
            exp = term.exp if isinstance(term.exp, Number) else term.exp.coef
            if exp < 0:
                den.append(str(type(term)(value=term.value, exp=abs(term.exp))))
            else:
                num.append(str(term))
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
        val = Product(i**b.value for i in a.value)
        if not isinstance(b.value.value, Number) or not isinstance(b.value.exp, Number):
            if a.coef != 1:
                set.add(val, type(a)(value=a.coef, exp=b.value))
            return type(a)(value=Product(val))
        return type(a)(a.coef**b.value.value, val)

    @staticmethod
    def resolve(a, b):
        c = a.coef * b.coef
        a = type(a)(value=a.value, exp=a.exp)
        b = type(a)(value=b.value, exp=b.exp)
        return type(a)(c, Product([a, b]))

    @staticmethod
    def simplify(a, b):
        terms = a.copy()
        rem = (b.value if isinstance(b.value, Product) else {b}).copy()
        for a in tuple(terms):
            for b in tuple(rem):
                if not terms:
                    break
                if a.like(b, 0):
                    terms.remove(a)
                    rem.remove(b)
                    a *= b
                    if a.value != 1:
                        terms.add(a)
        return terms.union(rem)
