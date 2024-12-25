from .classes import *
from .constants import SYMBOLS


def _clean(args):
    args = list(args)
    from data_types.term import Term, Number

    for idx, term in enumerate(args):
        coef, value, exp = term.coef, term.value, term.exp
        while isinstance(value, Term) and exp == 1:
            coef, value, exp = coef * value.coef, value.value, value.exp
        if coef == 0:
            value = Number(0)
            exp = Number(1)
        elif exp == 0:
            value, exp = (Number(1),) * 2
        args[idx] = Term(coef, value, exp)
    return args


def clean(func):
    def cleaned(*args):
        return _clean([func(*_clean(args))]).pop()

    return cleaned


def standard_form(collection):
    from data_types.bases import Number, Variable

    def key(v):
        res = 0
        if isinstance(v.exp, Number):
            res = v.exp * 100 * (not isinstance(v.value, Number))
        if isinstance(v.value, Variable):
            res += ord(v.value) / 50
        res += min(v.coef, 10)
        return res + (not isinstance(v.exp, Number))

    return sorted(collection, key=key, reverse=1)
