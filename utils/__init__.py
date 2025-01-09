from .classes import *


def lexicographic_weight(algebraobject):
    from data_types import Number, Variable, Collection

    if isinstance(algebraobject.value, Number) or not isinstance(
        algebraobject.exp, Number
    ):
        return Number(0)
    res = Number(0)

    if isinstance(algebraobject.value, Collection) and algebraobject.exp == 1:
        # Calling sum() does not work
        for t in algebraobject.value:
            res += lexicographic_weight(t)
        return res
    res = algebraobject.exp
    if isinstance(algebraobject.value, Variable):
        res += ord(algebraobject.value) * 0.001
    return res


def standard_form(collection):
    return sorted(collection, key=lexicographic_weight, reverse=1)


def print_frac(frac):
    if any(not frac.denominator % i for i in (2, 5)) and frac.denominator % 3:
        return str(frac.numerator / frac.denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return str(frac).join("()")
