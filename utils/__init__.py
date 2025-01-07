from .classes import *


def lexicographic_weight(alebgraobject):
    from data_types import Number, Variable, Collection

    if isinstance(alebgraobject.value, Number) or not isinstance(
        alebgraobject.exp, Number
    ):
        return Number(0)
    res = alebgraobject.exp

    if isinstance(alebgraobject.value, Collection) and alebgraobject.exp == 1:
        # Calling sum() does not work
        for t in alebgraobject.value:
            res += lexicographic_weight(t)
        return res
    if isinstance(alebgraobject.value, Variable):
        res += ord(alebgraobject.value) * 0.001
    return res


def standard_form(collection):
    return sorted(collection, key=lexicographic_weight, reverse=1)


def print_frac(frac):
    if any(not frac.denominator % i for i in (2, 5)) and frac.denominator % 3:
        return str(frac.numerator / frac.denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return str(frac).join("()")
