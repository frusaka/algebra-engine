from dataclasses import dataclass
from typing import Any
from .tokens import Token
from utils.constants import SYMBOLS


@dataclass(frozen=True)
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Token
    value: Any

    def __repr__(self) -> str:
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass(frozen=True)
class Binary:
    """Unary operator: arithmetic (+-*/) or exponetiation"""

    oper: Token
    left: Any
    right: Any

    def __repr__(self) -> str:
        return f"({self.left} {SYMBOLS.get(self.oper.type.name)} {self.right})"
