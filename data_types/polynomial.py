from functools import singledispatchmethod
from itertools import chain
from .bases import Collection
from utils import standard_form


class Polynomial(Collection):
    def __init__(self, terms):
        super().__init__(self.merge(chain(*map(self.flatten, terms))))

    def __str__(self):
        res = ""
        for idx, term in enumerate(standard_form(self)):
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
    @staticmethod
    def add(b, a):
        val = Polynomial([b.value, a])
        if len(val) == 1:
            return val.pop()
        return type(a)(value=val)

    @singledispatchmethod
    @staticmethod
    def mul(b, a):
        if a.exp != 1:
            return
        return type(a)(value=Polynomial(term * b.value for term in a.value))

    @staticmethod
    def merge(terms):
        terms = list(terms)
        res = []
        while terms:
            term = terms.pop(0)
            found = 0
            for other in tuple(terms):
                if term.like(other):
                    if (val := (term + other)).value != 0:
                        res.append(val)
                    terms.remove(other)
                    found = 1
            if not found:
                res.append(term)
        return res
