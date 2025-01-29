from .collection import Collection
from .term import Term


class Solutions(Collection):
    """
    A collection of valid outputs for a given expression.
    NOTE: Still under developement
    """

    def __add__(self, value: Term):
        return Solutions(t + value for t in self)

    def __sub__(self, value: Term):
        return Solutions(t - value for t in self)

    def __mul__(self, value: Term):
        return Solutions(t * value for t in self)

    def __truediv__(self, value: Term):
        return Solutions(t / value for t in self)

    def __pow__(self, value: Term):
        return Solutions(t**value for t in self)

    def __str__(self) -> str:
        return ", ".join(str(t) for t in self).join("{}")

    @property
    def value(self):
        return self
