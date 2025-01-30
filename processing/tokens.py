from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    """Supported token types"""

    # Comparison
    GETITEM = 0
    BOOL = 1

    EQ, NE, GT, GE, LT, LE = 2, 2.2, 2.4, 2.6, 2.8, 2.9

    NUMBER, VAR = 3, 3.2
    ADD, SUB = 4, 4.2
    MUL, TRUEDIV = 5, 5.2
    POS, NEG = 6, 6.2
    POW, ROOT = 7, 7.2

    LPAREN, RPAREN = -8, -8.2
    ERROR = -9


@dataclass
class Token:
    """Lexer representation of a token. Contains precedence data"""

    type: TokenType
    value: Any = None
    iscoef: bool = False

    def __repr__(self):
        return self.type.name + (f": {self.value}" if self.value is not None else "")

    @property
    def priority(self):
        return self.type.value // 1 + self.iscoef * 0.2
