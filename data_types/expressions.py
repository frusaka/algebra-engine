from utils.classes import expression, factor, number
from utils.utils import Proxy
from .bases import Collection
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
                return type(a)(value=terms)

    @add.register(expression)
    def _(_, b, a):
        b = b.value
        if a.like(b):
            return type(a)(value=[*a.value, *b.value], exp=a.exp)

    @singledispatchmethod
    def mul(_, b, a):
        b = b.value
        return type(a)(value=Expression(term * b for term in a.value), exp=a.exp)

    @mul.register(factor)
    def _(_, b, a):
        return _.mul(b, a) * type(a)(value=b.value.coef)


# @dataclass
class Factor(Collection):
    def __hash__(self):
        return hash((type(self), tuple(self)))

    def __init__(self, terms, merge_action="mul"):
        super().__init__(terms, merge_action)

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
        b = b.value
        if b.exp < 0:
            c = a.coef * b.coef
            ca, cb = _.simplify(type(a)(value=b.value, exp=-b.exp))
            if not ca and not cb:
                return type(a)()
            if ca:
                ca = type(a)(c, ca, a.exp)
            if cb:
                cb = type(a)(value=cb, exp=-b.exp)

            if not ca or not cb:
                return ca or cb
            return type(a)(value=Expression([ca, cb]), exp=a.exp)
        return type(a)(
            a.coef * b.coef,
            Factor(list(a.value) + [type(a)(value=b.value, exp=b.exp)]),
            a.exp,
        )

    @mul.register(number)
    def _(_, b, a):
        b = b.value
        return type(a)(a.coef * b.value, a.value, a.exp)

    @mul.register(expression)
    def _(_, b, a):
        return b.value.mul(Proxy(a, factor), b.value)

    @mul.register(factor)
    def _(_, b, a):
        return type(a)(a.coef * b.value.coef, Factor([*a.value, *b.value.value]))

    def simplify(a, b):
        terms = a.copy()
        rem = (b.value if isinstance(b.value, Factor) else {b}).copy()
        for j in tuple(rem):
            if j in terms:
                terms.remove(j)
                rem.remove(j)

        if len(rem) == 1:
            rem = rem.pop()
        elif rem:
            rem = Factor(rem)
        if len(terms) == 1:
            res = terms.pop()
        elif terms:
            res = Factor(terms)
        return res, rem
