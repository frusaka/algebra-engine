import itertools
from .collection import Collection
from .number import Number
from utils import lexicographic_weight, standard_form, dispatch, polynomial


class Polynomial(Collection):
    def __new__(cls, algebraobjects):
        return super().__new__(
            cls,
            cls.merge(
                itertools.chain(
                    *itertools.starmap(
                        cls.flatten, zip(algebraobjects, itertools.repeat(cls))
                    )
                ),
            ),
        )

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
            return next(iter(val))
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
        from .product import Product

        b = b.value
        if a.exp == 1:
            res = Polynomial(t * b for t in a.value)
            if not res:
                return type(a)(value=Number(0))
            if len(res) == 1:
                return next(iter(res))
            return type(a)(value=res)
        if a.like(b, 0):
            return type(a)(
                a.coef * b.coef, a.value, type(a)(value=a.exp) + type(a)(value=b.exp)
            )
        if isinstance(b.value, Polynomial) and b.exp == 1:
            return b * a
        if a.exp == -1:
            num, den = a.rationalize(b, a ** -type(a)())
            if isinstance(num.value, Number) and num.exp == 1:
                return type(a)(num.value, den.value, a.exp)
            return Product.resolve(num, den ** -type(a)())
        if isinstance(a.exp, Number) and isinstance(b.value, Number) and b.exp == 1:
            return type(a)(b.value * a.coef, a.value, a.exp)

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
    def _long_division(a, b):
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
            if not isinstance(a.value, Polynomial) or a.exp != 1:
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

    @staticmethod
    def long_division(a, b):
        # Supports dual direction long division
        from .product import Product

        if lexicographic_weight(b, 0) > lexicographic_weight(a, 0) and isinstance(
            b.value, Polynomial
        ):
            res = Polynomial._long_division(b, a)
            a, b = a.rationalize(type(a)(), res)
            if isinstance(a.value, Number) and a.exp == 1:
                return type(a)(a.value * b.coef, b.value, -b.exp)
            return Product.resolve(a, b ** -type(a)())
        return Polynomial._long_division(a, b)

    @staticmethod
    def merge(algebraobjects):
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
                # Combining fractions
                if not isinstance(a.denominator.value, Number) and not isinstance(
                    b.denominator.value, Number
                ):
                    den = a.lcm(a.denominator, b.denominator)
                    num_a = (den / a.denominator) * a.numerator
                    num_b = (den / b.denominator) * b.numerator
                    v = (num_a + num_b) / den
                    ls.remove(b)
                    return Polynomial.merge(
                        itertools.chain(ls, res, Polynomial.flatten(v, Polynomial))
                    )
            else:
                res.append(a)
        return res
