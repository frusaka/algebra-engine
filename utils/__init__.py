from .classes import *


def standard_form(collection):
    from data_types import Number, Variable

    def key(v):
        res = 0
        if isinstance(v.exp, Number):
            res = v.exp**3
        if isinstance(v.value, Variable):
            res += ord(v.value) / 100
        return res

    return sorted(collection, key=key, reverse=1)


def print_frac(frac):
    if any(not frac.denominator % i for i in (2, 5)) and frac.denominator % 3:
        return str(frac.numerator / frac.denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return str(frac).join("()")
