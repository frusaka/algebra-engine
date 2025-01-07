from itertools import chain
from .collection import Collection
from .number import Number
from utils import standard_form, dispatch, polynomial


class Polynomial(Collection):
    def __init__(self, algebraobjects):
        super().__init__(self.merge(chain(*map(self.flatten, algebraobjects))))

    def __str__(self):
        res = ""
        for idx, algebraobject in enumerate(standard_form(self)):
            rep = str(algebraobject)
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
            res = Polynomial(algebraobject * b for algebraobject in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return res.pop()
            return type(a)(value=res)
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )
        if isinstance(b.value, Number) and b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)
        if isinstance(b.value, Polynomial) and b.exp == 1:
            return b * a

    @property
    def leading(self):
        return max(self, key=lambda x: x.exp * (not isinstance(x.value, Number)))

    @staticmethod
    def long_division(a, b):
        # Only works with univariate Polynomials
        from .product import Product
        from .algebraobject import AlgebraObject

        if a.exp != 1 or b.exp != 1:
            return a * b ** -AlgebraObject()
        org = a
        leading_b = b.value.leading
        res = AlgebraObject(Number(0))
        while a.value:
            # Remainder
            if (
                not isinstance(a.value, Polynomial)
                or leading_b.exp > (leading_a := a.value.leading).exp
            ):
                res += a * b ** -AlgebraObject()
                break
            fac = leading_a / leading_b
            # Polynomials are indivisible or due to algorithm not using lexicographic ordering
            if isinstance(fac.value, Product) and (
                not isinstance(leading_a.value, Product)
                or len(fac.value) > len(leading_a.value)
            ):
                # raise NotImplementedError("Input Polynomials out of expected domain")
                return org * b ** -AlgebraObject()
            res += fac
            a -= fac * b
        return res

    @staticmethod
    def merge(algebraobjects):
        algebraobjects = list(algebraobjects)
        while algebraobjects:
            a = algebraobjects.pop(0)
            if a.value == 0:
                continue
            for b in tuple(algebraobjects):
                if a.like(b):
                    if (val := (a + b)).value != 0:
                        yield val
                    algebraobjects.remove(b)
                    break
            else:
                yield a

    def flatten(self, algebraobject):
        if algebraobject.exp != 1 or not isinstance(algebraobject.value, Polynomial):
            yield algebraobject
            return

        for i in algebraobject.value:
            yield from self.flatten(i)
