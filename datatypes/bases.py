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

    def ast_subs(self, mapping: dict):
        pass
