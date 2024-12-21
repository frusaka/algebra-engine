from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    EQ = 0
    NE = 0.2
    GT = 0.4
    GE = 0.6
    LT = 0.8
    LE = 1

    NUMBER = 2
    VAR = 3
    SUB = 4
    ADD = 5
    TRUEDIV = 6
    MUL = 8  # For the cases of variables (4x/5y should be (4 * x) / (5 * y), not ((4 * x) / 5) * y)
    POW = 10
    ROOT = 11
    NEG = 12
    POS = 13
    LPAREN = -11
    RPAREN = -12


@dataclass
class Token:
    type: TokenType
    value: Any = None

    def __repr__(self):
        return self.type.name + (f": {self.value}" if self.value is not None else "")

    @property
    def priority(self):
        return max(0, self.type.value // 2)

    @property
    def is_operator(self):
        return self.type.value >= 4
