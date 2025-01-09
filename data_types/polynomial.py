from itertools import chain
from .collection import Collection
from .number import Number
from utils import lexicographic_weight, standard_form, dispatch, polynomial


class Polynomial(Collection):
    def __init__(self, algebraobjects):
        res = chain(*map(self.flatten, algebraobjects))
        # Tripple merge in case of addition by like denominator
        for _ in range(3):
            res = self.merge(res)
        super().__init__(res)

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

    @staticmethod
    def long_division(a, b):
        from .product import Product
        from .algebraobject import AlgebraObject

        if a.exp != 1 or b.exp != 1:
            # return a * b ** -AlgebraObject()
            return Product.resolve(a, b ** -AlgebraObject())
        leading_b = b
        if isinstance(b.value, Polynomial):
            leading_b = b.value.leading
        org = a
        res = AlgebraObject(Number(0))
        while a.value:
            # Remainder
            if not isinstance(a.value, Polynomial) or (
                lexicographic_weight(b) > lexicographic_weight(a)
            ):
                if isinstance(a.value, Polynomial):
                    res += Product.resolve(a, b ** -AlgebraObject())
                else:
                    res += a * b ** -AlgebraObject()
                break
            leading_a = a.value.leading
            fac = leading_a / leading_b
            if isinstance(fac.value, Product) and (
                not isinstance(leading_a.value, Product)
                or len(fac.value) > len(leading_a.value)
            ):
                return Product.resolve(org, b ** -AlgebraObject())
            res += fac
            a -= fac * b
        return res

    @staticmethod
    def merge(algebraobjects):
        res = list(algebraobjects)
        while res:
            a = res.pop(0)
            if a.value == 0:
                continue
            for b in tuple(res):
                if a.like(b):
                    if (val := (a + b)).value != 0:
                        yield val
                    res.remove(b)
                    break
                if a.denominator.value == b.denominator.value and not isinstance(
                    a.denominator.value, Number
                ):
                    v = (a.numerator + b.numerator) / a.denominator
                    yield from Polynomial.flatten(v)
                    res.remove(b)
                    break
            else:
                yield a

    @staticmethod
    def flatten(algebraobject):
        if algebraobject.exp != 1 or not isinstance(algebraobject.value, Polynomial):
            yield algebraobject
            return

        for i in algebraobject.value:
            yield from Polynomial.flatten(i)
