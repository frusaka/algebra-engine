from dataclasses import dataclass
from functools import lru_cache

from .tokens import TokenType
from utils.constants import SYMBOLS
from . import operators
from datatypes import System


class Node:
    @lru_cache
    def eval(self):
        return self._eval()


class Tuple(Node, tuple):
    def _eval(self) -> tuple:
        return self


class Sys(Node, frozenset):
    def _eval(self) -> System:
        return System(i.eval() for i in self)


@dataclass(frozen=True)
class Unary(Node):
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: TokenType
    value: Node

    def __repr__(self) -> str:
        return f"{SYMBOLS.get(self.oper.name)}{self.value}"

    def eval(self):
        return getattr(operators, self.oper.lower())(self.value.eval())


@dataclass(frozen=True)
class Binary(Node):
    """Binary operator: arithmetic (+-*/) or exponetiation"""

    oper: str
    left: Node
    right: Node

    def __repr__(self) -> str:
        return f"({self.left} {SYMBOLS.get(self.oper)} {self.right})"

    def _eval(self):
        left = self.left
        right = self.right.eval()
        if self.oper != "SOLVE":  # Do not convert lhs to Term when solving
            left = left.eval()
        return getattr(operators, self.oper.lower())(left, right)
