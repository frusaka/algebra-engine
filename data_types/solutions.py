import itertools
from .collection import Collection
from .term import Term
from .number import Number


def plus_minus_key(t: Term) -> Term:
    if not isinstance(t.value, Number) or not t.value.numerator.imag:
        return abs(t)
    return t


class Solutions(Collection):
    """
    A collection of valid outputs for a given equation or inequality
    """

    def __add__(self, value: Term):
        return Solutions(t + value for t in self)

    def __sub__(self, value: Term):
        return Solutions(t - value for t in self)

    def __mul__(self, value: Term):
        return next(iter(v)) if len(v := Solutions(t**value for t in self)) == 1 else v

    def __truediv__(self, value: Term):
        return Solutions(t / value for t in self)

    def __pow__(self, value: Term):
        return next(iter(v)) if len(v := Solutions(t**value for t in self)) == 1 else v

    def __str__(self) -> str:
        res = []
        for i, vals in itertools.groupby(self, key=plus_minus_key):
            if len(list(vals)) == 1:
                res.append(str(i))
            else:
                res.append("±" + str(i))
        return " and ".join(res)

    @property
    def value(self):
        return self
