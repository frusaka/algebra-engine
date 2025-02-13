import itertools
from .collection import Collection
from .term import Term
from .number import Number


def plus_minus_key(t: Term) -> Term:
    if not isinstance(t.value, Number) or not t.value.numerator.imag:
        return abs(t)
    return t


class System(Collection):
    """A system of equations or inequalities"""

    def __getitem__(self, value):
        """Solve for a system of (in)equalities"""
        print(self)
        return self

    def __add__(self, value: Term):
        return System(t + value for t in self)

    def __sub__(self, value: Term):
        return System(t - value for t in self)

    def __mul__(self, value: Term):
        return next(iter(v)) if len(v := System(t * value for t in self)) == 1 else v

    def __truediv__(self, value: Term):
        return System(t / value for t in self)

    def __pow__(self, value: Term):
        return next(iter(v)) if len(v := System(t**value for t in self)) == 1 else v

    def __str__(self) -> str:
        return ", ".join((str(i) for i in self))

    @property
    def value(self):
        return self
