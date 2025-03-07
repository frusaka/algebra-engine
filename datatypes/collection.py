from __future__ import annotations
from typing import Generator, TYPE_CHECKING
from .bases import *

if TYPE_CHECKING:
    from .term import Term


class Collection(Unknown, frozenset, Atomic):
    """
    A base class representing a collection of unique terms
    """

    def __hash__(self) -> int:
        return frozenset.__hash__(self)

    def __str__(self):
        if not self:
            return "∅"
        if len(self) == 1:
            return str(next(iter(self)))
        return ", ".join(str(i) for i in self).join("{}")

    @classmethod
    def flatten(cls, term: Term) -> Generator[Term, None, None]:
        """Unnest the given term if the type matches the `cls`"""
        if term.exp != 1 or not term.value.__class__ is cls:
            yield term
            return

        for i in term.value:
            yield from cls.flatten(i)
