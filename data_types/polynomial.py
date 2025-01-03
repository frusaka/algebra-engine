from itertools import chain
from .bases import Collection, Number
from utils import standard_form, dispatch, polynomial


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

    @staticmethod
    def resolve(b, a):
        val = Polynomial([b.value, a])
        if not val:
            return type(a)(value=Number(0))
        if len(val) == 1:
            return val.pop()
        return type(a)(value=val)

    @dispatch
    def add(b, a):
        return Polynomial.resolve(b, a)

    @add.register(polynomial)
    def _(b, a):
        if a.like(b.value) and a.exp != 1:
            return type(a)(a.coef + b.value.coef, a.value, a.exp)
        return Polynomial.resolve(b, a)

    @dispatch
    def mul(b, a):
        b = b.value
        if a.exp == 1:
            res = Polynomial(term * b for term in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return res.pop()
            return type(a)(value=res)
        if a.like(b, 0):
            return type(a)(a.coef * b.coef, a.value, a.exp + b.exp)
        if isinstance(b.value, Number) and b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

    @property
    def leading(self):
        return max(self, key=lambda x: x.exp * (not isinstance(x.value, Number)))

    @staticmethod
    def long_division(a, b):
        # Only works with univariate Polynomials
        from .product import Product
        from .term import Term

        if a.exp != 1 or b.exp != 1:
            return type(a)(value=Product([a, b ** -Term()]))
        leading_b = b.value.leading
        res = []
        while a.value:
            # Remainder
            if (
                not isinstance(a.value, Polynomial)
                or leading_b.exp > (leading_a := a.value.leading).exp
            ):
                res.append(a * b ** -Term())
                break
            fac = leading_a / leading_b
            if isinstance(fac.value, Product) and (
                not isinstance(leading_a.value, Product)
                or len(fac.value) > len(leading_a.value)
            ):
                raise NotImplementedError("Input Polynomials out of expected domain")
            res.append(fac)
            a -= fac * b
        if len(res) == 1:
            return res.pop()
        return Term(value=Polynomial(res))

    @staticmethod
    def merge(terms):
        terms = list(terms)
        while terms:
            a = terms.pop(0)
            if a.value == 0:
                continue
            for b in tuple(terms):
                if a.like(b):
                    if (val := (a + b)).value != 0:
                        yield val
                    terms.remove(b)
                    break
            else:
                yield a

    def flatten(self, term):
        if term.exp != 1 or not isinstance(term.value, Polynomial):
            yield term
            return

        for i in term.value:
            yield from self.flatten(i)
