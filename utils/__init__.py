from .classes import *


def standard_form(collection):
    from data_types.bases import Number, Variable

    B = max(collection, key=lambda x: x.coef).coef

    def key(v):
        res = 0
        if isinstance(v.exp, Number):
            res = v.exp * 100 * (not isinstance(v.value, Number))
        if isinstance(v.value, Variable):
            res += ord(v.value) / 50
        return res + (v.coef - 0.8) / (B - 0.8) * 3.2 + 0.8

    return sorted(collection, key=key, reverse=1)
