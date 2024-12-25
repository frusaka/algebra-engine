from functools import singledispatchmethod
from .bases import Collection, Number
from .polynomial import Polynomial
from utils import *


class Factor(Collection):
    def __str__(self):
        num, den = [], []
        for term in reversed(standard_form(self)):
            exp = term.exp if isinstance(term.exp, Number) else term.exp.coef
            if exp < 0:
                den.append(str(type(term)(value=term.value, exp=abs(term.exp))))
            else:
                num.append(str(term))
        a, b = " • ".join(num), " • ".join(den)
        # a, b = "".join(num), "".join(den)
        if len(num) > 1:
            a = a.join("()")
        if len(den) > 1:
            b = b.join("()")
        if not num:
            return f"1/{b}".join("()")
        if den:
            return f"{a}/{b}".join("()")
        return a

    def like(self, other):
        if not isinstance(other, Factor):
            return 0
        return super(self) == other

    @singledispatchmethod
    def add(_, b, a):
        b = b.value
        if a.like(b):
            return type(a)(a.coef + b.coef, a.value, a.exp)

    @singledispatchmethod
    def mul(_, b, a):
        pass

    @mul.register(factor | variable)
    def _(_, b, a):
        b = b.value
        if not isinstance(a.exp, Number) or not isinstance(b.exp, Number):
            return
        c = a.coef * b.coef
        res = Factor.simplify(a.value, type(a)(value=b.value, exp=b.exp))
        if res:
            return type(a)(c, res.pop() if len(res) == 1 else Factor(res))
        return type(a)(value=c)

    @mul.register(number)
    def _(_, b, a):
        if b.value.exp != 1:
            return
        return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial)
    def _(_, b, a):
        return Polynomial.mul(_, Proxy(a, factor), b.value)

    @singledispatchmethod
    def pow(_, b, a):
        val = Factor(i**b.value for i in a.value)
        if not isinstance(b.value.value, Number) or not isinstance(b.value.exp, Number):
            if a.coef != 1:
                set.add(val, type(a)(value=a.coef, exp=b.value))
            return type(a)(value=Factor(val))
        return type(a)(a.coef**b.value.value, val)

    @staticmethod
    def simplify(a, b):
        terms = a.copy()
        rem = (b.value if isinstance(b.value, Factor) else {b}).copy()
        for i in tuple(terms):
            for j in tuple(rem):
                if not terms:
                    break
                if i.like(j, 0):
                    terms.remove(i)
                    rem.remove(j)
                    i *= j
                    if not isinstance(i.value, Number):
                        terms.add(i)
        return terms.union(rem)
