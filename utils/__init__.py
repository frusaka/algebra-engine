from .classes import *


def lexicographic_weight(term, alphabetic=True):
    from data_types import Number, Variable, Collection

    if isinstance(term.value, Number) or not isinstance(term.exp, Number):
        return Number(0)
    res = Number(0)

    if isinstance(term.value, Collection) and term.exp == 1:
        # Calling sum() does not work
        for t in term.value:
            res += lexicographic_weight(t, alphabetic)
        return res
    res = term.exp
    if isinstance(term.value, Variable) and alphabetic:
        # Map range formula
        a, b = ord("A"), ord("z")
        c, d = 0, 0.1
        x = ord(term.value)
        res += c + ((x - a) * (d - c)) / (b - a)
    return res


def standard_form(collection):
    return sorted(collection, key=lexicographic_weight, reverse=1)


def print_frac(frac):
    denominator = frac.denominator
    if denominator == 1:
        return str(frac.numerator)
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if denominator == 1:
        return str(frac.numerator / frac.denominator)
    return "/".join((str(frac.numerator), str(frac.denominator)))


def print_coef(coef):
    res = ""
    if coef != 1:
        res = str(coef)
        if not coef.numerator.real:
            res = res.join("()")
    if coef == -1:
        res = "-"
    return res
