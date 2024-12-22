from utils.classes import expression, factor, number, variable
from utils.utils import Proxy
from .bases import Collection, Number
from functools import singledispatchmethod


class Expression(Collection):
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


# @dataclass
class Factor(Collection):
    def __init__(self, terms):
        super().__init__(terms, "mul")

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

    @mul.register(factor)
    def _(_, b, a):
        b = b.value
        c = a.coef * b.coef
        if b.exp < 0:
            ca, cb = _.simplify(type(a)(value=b.value, exp=-b.exp))
            if ca and cb:
                return type(a)(c, Factor([ca, cb]), a.exp)
            if not ca and not cb:
                return type(a)(value=c)
            if ca:
                return type(a)(c, ca, a.exp)
            return type(a)(c, value=cb, exp=-b.exp)
        return type(a)(c, Factor([*a.value, *b.value]), a.exp)

    @mul.register(number)
    def _(_, b, a):
        b = b.value
        return type(a)(a.coef * b.value, a.value, a.exp)

    @mul.register(variable)
    def _(_, b, a):
        b = b.value
        return type(a)(
            a.coef * b.coef, Factor([*a.value, type(a)(value=b.value, exp=b.exp)])
        )

    @mul.register(expression)
    def _(_, b, a):
        return b.value.mul(Proxy(a, factor), b.value)

    def simplify(a, b):
        terms = a.copy()
        rem = (b.value if isinstance(b.value, Factor) else {b}).copy()
        for j in tuple(rem):
            if j in terms:
                terms.remove(j)
                rem.remove(j)
        res = None
        if len(rem) == 1:
            rem = rem.pop()
        elif rem:
            rem = Factor(rem)
        if len(terms) == 1:
            res = terms.pop()
        elif terms:
            res = Factor(terms)
        return res, rem
