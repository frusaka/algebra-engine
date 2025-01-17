from dataclasses import dataclass
from typing import Any
from utils.constants import SYMBOLS


@dataclass
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Any
    value: Any

    def __repr__(self):
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass
class Binary:
    """Unary operator: arithmetic (+-*/) or exponetiation"""

    oper: Any
    left: Any
    right: Any

    def __repr__(self):
        return f"({self.left} {SYMBOLS.get(self.oper.type.name)} {self.right})"
