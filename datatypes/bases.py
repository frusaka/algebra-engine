from __future__ import annotations
from typing import Any, TYPE_CHECKING
from fractions import Fraction
from utils import Proxy

if TYPE_CHECKING:
    from .term import Term


class Atomic:
    """Base class for all atomic objects"""

    def like(self, other: Any) -> bool:
        return self == other

    @staticmethod
    def poly_pow(b: Proxy[Term], a: Term) -> Term | None:
        b = b.value
        if b.exp != 1:
            return
        res = type(a)()
        for i in b.value:
            res *= a**i
        return res

    def eval(self) -> Term:
        # From parsing the stage to evaluation stage
        from .term import Term

        return Term(value=self)


class Unknown:
    """
    A small class that prevents comparsions between unknowns.
    This class should be removed and better alternatives developed
    """

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value) and type(value) is type(self)

    def __gt__(self, value: Any) -> bool:
        return False

    def __lt__(self, value: Any) -> bool:
        return False

    def __ge__(self, value: Any) -> bool:
        return self == value

    def __le__(self, value: Any) -> bool:
        return self == value
