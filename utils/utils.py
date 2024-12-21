class Proxy:
    def __init__(self, value, fake):
        self.value = value
        self._fake = fake

    @property
    def __class__(self):
        return self._fake


def clean(*args, **kwargs):
    args = list(args)
    from data_types.term import Term

    for idx, term in enumerate(args):
        while isinstance(term.value, Term) and term.exp == 1 and term.coef == 1:
            term = Term(term.value.coef, term.value, term.value.exp)
        args[idx] = term

    for k, term in kwargs.values():
        while (
            isinstance(term.value, Term)
            and term.exp == 1
            and term.exp == 1
            and term.coef == 1
        ):
            term = Term(term.value.coef, term.value, term.value.exp)
        kwargs[k] = term
    return args, kwargs


def flatten(func):
    def cleaned(*args, **kwargs):
        args, kwargs = clean(*args, *kwargs)
        return clean(func(*args, **kwargs))[0][0]

    return cleaned


def standard_form(collection):
    from data_types.bases import Number, Variable

    def key(v):
        res = v.exp * 10000 * (not isinstance(v.value, Number))
        if isinstance(v.value, Variable):
            res += ord(v.value) / 10
        res += min(v.coef, 100)
        return res

    return sorted(collection, key=key, reverse=1)
