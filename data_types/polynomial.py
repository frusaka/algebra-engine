from itertools import chain
from .collection import Collection
from .number import Number
from utils import lexicographic_weight, standard_form, dispatch, polynomial


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
            res = Polynomial(t * b for t in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return res.pop()
            return type(a)(value=res)
        elif type(b.value).__name__ == "Product":
            return b * a
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
        return max(self, key=lexicographic_weight)

    def leading_options(self):
        leading = self.leading
        return [
            i
            for i in self
            if lexicographic_weight(i, 0) == lexicographic_weight(leading, 0)
        ]

    @staticmethod
    def long_division(a, b):
        from .product import Product
        from .algebraobject import AlgebraObject

        if a.exp != 1 or b.exp != 1:
            return Product.resolve(a, b ** -AlgebraObject())
        leading_b = b
        options_b = []
        if isinstance(b.value, Polynomial):
            options_b = b.value.leading_options()
            leading_b = options_b.pop()

        org = a
        res = AlgebraObject(Number(0))
        while a.value:
            # Remainder
            if not isinstance(a.value, Polynomial):
                res += a * b ** -AlgebraObject()
                break
            for leading_a in a.value.leading_options():
                fac = leading_a / leading_b
                if (
                    isinstance(fac.denominator.value, Number)
                    and fac.denominator.exp == 1
                ):
                    break
            else:
                if not res.value and options_b:
                    leading_b = options_b.pop()
                    a = org
                    res = AlgebraObject(Number(0))
                    continue
                res += Product.resolve(a, b ** -AlgebraObject())
                break
            res += fac
            a -= fac * b
        return res

    def merge(self, algebraobjects):
        ls = list(algebraobjects)
        res = []
        while ls:
            a = ls.pop(0)
            if a.value == 0:
                continue
            for b in ls:
                if a.like(b):
                    if (val := (a + b)).value != 0:
                        res.append(val)
                    ls.remove(b)
                    break
                if a.denominator.value == b.denominator.value and not isinstance(
                    a.denominator.value, Number
                ):
                    v = (a.numerator + b.numerator) / (
                        a.denominator * type(a)(b.denominator.coef)
                    )
                    ls.remove(b)
                    return self.merge(chain(ls, res, self.flatten(v)))
            else:
                res.append(a)
        return res

    @staticmethod
    def flatten(algebraobject):
        if algebraobject.exp != 1 or not isinstance(algebraobject.value, Polynomial):
            yield algebraobject
            return

        for i in algebraobject.value:
            yield from Polynomial.flatten(i)
