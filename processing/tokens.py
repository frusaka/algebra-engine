from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    EQ, NE, GT, GE, LT, LE = 0, 0.2, 0.4, 0.6, 0.8, 0.9

    NUMBER, VAR = 1, 1.2
    ADD, SUB = 2, 2.2
    MUL, TRUEDIV = 3, 3.2
    POW, ROOT = 5, 5.2
    POS, NEG = 4, 4.2

    LPAREN, RPAREN = -6, -6.2
    ERROR = -7


@dataclass
class Token:
    type: TokenType
    value: Any = None
    iscoef: bool = False

    def __repr__(self):
        return self.type.name + (f": {self.value}" if self.value is not None else "")

    @property
    def priority(self):
        return self.type.value // 1 + self.iscoef * 0.2
