from __future__ import annotations
from .bases import *
from typing import Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from .term import Term


class Collection(Unknown, frozenset, Atomic):
    """
    A base class representing a collection of unique terms
    """

    def __hash__(self) -> int:
        return frozenset.__hash__(self)

    @classmethod
    def flatten(cls, term: Term) -> Generator[Term, None, None]:
        """Unnest the given term if the type matches the `cls`"""
        if term.exp != 1 or not isinstance(term.value, cls):
            yield term
            return

        for i in term.value:
            yield from cls.flatten(i)
