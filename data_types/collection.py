from .bases import *
from utils import *


class Collection(Unknown, frozenset, Base):
    """
    A base class representing a collection of unique terms
    """

    def __hash__(self):
        return frozenset.__hash__(self)

    @classmethod
    def flatten(cls, algebraobject):
        """Unnest the given term if the type matches the `cls`"""
        if algebraobject.exp != 1 or not isinstance(algebraobject.value, cls):
            yield algebraobject
            return

        for i in algebraobject.value:
            yield from cls.flatten(i)