from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    """Supported token types"""

    COMMA = 0
    SOLVE = 1

    EQ, GT, GE, LT, LE = 4, 4.2, 4.4, 4.6, 4.8
    CONST, VAR = 5, 5.2

    ADD, SUB = 7, 7.2
    MUL, TRUEDIV = 8, 8.2
    POS, NEG = 9, 9.2
    POW, SQRT = 10, 10.2
    GCD = 10.3
    LCM = 10.4
    FACTOR = 10.5
    EXPAND = 10.6
    APPROX = 10.7
    SUBS = 10.8

    LPAREN, RPAREN, LBRACK, RBRACK = -11, -11.2, -11.4, -11.6

    ERROR = -12

    def is_unary(self) -> bool:
        return self.name in {"POS", "NEG", "SQRT", *FUNCTIONS, "LBRACK"}


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


FUNCTIONS = tuple(tk.name for tk in TokenType if tk.value == 1 or tk.value > 10)
