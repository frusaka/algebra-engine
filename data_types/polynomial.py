from functools import singledispatchmethod
from itertools import chain
from .bases import Collection, Number
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
    def long_division(a, b):
        # Only works with univariate Polynomials
        # Needs to check if it is divisible in the first place
        from .factor import Factor
        from .term import Term

        if b.exp != 1 or a.exp != 1:
            return
        leading_b = max(
            b.value, key=lambda x: x.exp * (not isinstance(x.value, Number))
        )
        res = []
        while a.value:
            # Remainder
            if not isinstance(a.value, Polynomial):
                res.append(Term(value=Factor([a, b ** -Term()])))
                break
            leading_a = max(
                a.value, key=lambda x: x.exp * (not isinstance(x.value, Number))
            )
            fac = leading_a / leading_b
            res.append(fac)
            a -= fac * b
        return Term(value=Polynomial(res))

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
