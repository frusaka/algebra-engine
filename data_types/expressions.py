from functools import singledispatchmethod
from .bases import Collection, Number
from utils import *


class Expression(Collection):
    def __str__(self):
        res = ""
        for idx, term in enumerate(standard_form(self)):
            if term.value == 0:
                continue
            rep = str(term)
            if idx > 0 and res:
                if rep.startswith("-"):
                    rep = rep[1:]
                    res += " - "
                else:
                    res += " + "
            res += rep
        return res.join("()")

    @singledispatchmethod
    def add(_, b, a):
        b = b.value
        if a.exp != b.exp:
            return
        for term in a.value:
            if term.like(b):
                terms = a.value.copy()
                terms.remove(term)
                terms.add(term + b)
                if len(terms) == 1:
                    return terms.pop()
                return type(a)(value=Expression(terms))

    @add.register(expression)
    def _(_, b, a):
        b = b.value
        if a.like(b):
            return type(a)(value=Expression([*a.value, *b.value]), exp=a.exp)

    @singledispatchmethod
    def mul(_, b, a):
        if a.exp != 1:
            return
        b = b.value
        return type(a)(value=Expression(term * b for term in a.value), exp=a.exp)

    @mul.register(factor)
    def _(_, b, a):
        return _.mul(b, a) * type(a)(value=b.value.coef)


class Factor(Collection):
    def __init__(self, terms):
        super().__init__(terms, "mul")

    def __str__(self):
        num, den = [], []
        for term in reversed(standard_form(self)):
            if isinstance(term.exp, Number) and term.exp < 0:
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
            return type(a)(a.coef + b.coef, a, a.exp)

    @singledispatchmethod
    def mul(_, b, a):
        pass

    @mul.register(factor | variable)
    def _(_, b, a):
        b = b.value
        c = a.coef * b.coef

        if a.exp < 0:
            # TODO: Fix fraction logic
            # Both sides can be fractions, so can't simply reverse the input
            pass

        if b.exp < 0:
            ca, cb = _.simplify(a.value, type(a)(value=b.value, exp=-b.exp))
            if ca and cb:
                return type(a)(c, Factor([*ca, *cb]))
            if not ca and not cb:
                return type(a)(value=c)
            if ca:
                return type(a)(c, ca.pop() if len(ca) == 1 else Factor(ca), a.exp)
            return type(a)(c, cb.pop() if len(cb) == 1 else Factor(cb), -b.exp)

        if not isinstance(b.value, Factor):
            b = [b]
        else:
            b = b.value
        return type(a)(c, Factor([*a.value, *b]))

    @mul.register(number)
    def _(_, b, a):
        b = b.value
        return type(a)(a.coef * b.value, a.value, a.exp)

    @mul.register(expression)
    def _(_, b, a):
        return b.value.mul(Proxy(a, factor), b.value)

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
                    i /= j
                    if i.value != 1:
                        terms.add(i)
        return terms, rem
