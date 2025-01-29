from .bases import *
from utils import *


class Collection(Unknown, frozenset, Base):
    """
    A base class representing a collection of unique terms
    """

    def __hash__(self):
        return frozenset.__hash__(self)

    @classmethod
    def flatten(cls, term):
        """Unnest the given term if the type matches the `cls`"""
        if term.exp != 1 or not isinstance(term.value, cls):
            yield term
            return

        for i in term.value:
            yield from cls.flatten(i)
