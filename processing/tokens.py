from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    """Supported token types"""

    SOLVE = 0
    BOOL = 1

    EQ, NE, GT, GE, LT, LE = 2, 2.2, 2.4, 2.6, 2.8, 2.9

    NUMBER, VAR = 3, 3.2

    RATIO = 4

    ADD, SUB = 5, 5.2
    MUL, TRUEDIV = 6, 6.2
    POS, NEG = 7, 7.2
    POW, ROOT = 8, 8.2

    LPAREN, RPAREN = -9, -9.2
    ERROR = -10


@dataclass(frozen=True)
class Token:
    """Lexer representation of a token. Contains precedence data"""

    type: TokenType
    value: Any = None
    iscoef: bool = False

    def __repr__(self) -> str:
        return self.type.name + (f": {self.value}" if self.value is not None else "")

    @property
    def priority(self) -> float:
        return self.type.value // 1 + self.iscoef * 0.2
