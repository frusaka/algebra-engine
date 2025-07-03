from typing import Generator
from processing.tokens import Token, TokenType
from datatypes.nodes import Const, Var


class Lexer:
    """Takes input string and Tokenizes it"""

    OPERS = {
        "⟹": Token(TokenType.SOLVE),
        ",": Token(TokenType.COMMA),
        "=": Token(TokenType.EQ),
        ">": Token(TokenType.GT),
        "≥": Token(TokenType.GE),
        "<": Token(TokenType.LT),
        "≤": Token(TokenType.LE),
        "+": (Token(TokenType.ADD), Token(TokenType.POS)),
        "-": (Token(TokenType.SUB), Token(TokenType.NEG)),
        "*": (Token(TokenType.MUL), Token(TokenType.MUL, iscoef=True)),
        "/": Token(TokenType.TRUEDIV),
        "^": Token(TokenType.POW),
        "~": Token(TokenType.APPROX),
        "√": Token(TokenType.SQRT),
        "(": Token(TokenType.LPAREN),
        ")": Token(TokenType.RPAREN),
    }

    def __init__(self, expr: str) -> None:
        self.expr = iter(
            expr.replace(">=", "≥").replace("<=", "≤").replace("=>", "⟹").join("()")
        )
        self.advance()

    def advance(self) -> None:
        try:
            self.curr = next(self.expr)
        except StopIteration:
            self.curr = None

    def generate_tokens(self) -> Generator[Token, None, None]:
        """Generate tokens based on input string"""
        was_num = 0  # Disambiguate unary+- vs binary +-
        while self.curr is not None:
            if self.curr in " \n\t":  # Ignore spaces
                self.advance()
                continue

            if self.curr in "i." or self.curr.isdigit():
                # Can be toggled off to experiment with other notations (prefix & postfix)
                if was_num:
                    if self.curr != "i" and was_num != 1:
                        yield Token(
                            TokenType.ERROR,
                            SyntaxError(
                                "no operator between numbers"
                                if was_num == 3
                                else "variable preceeding digit"
                            ),
                        )
                        return
                    # Implicit multiplication - Parenthesis or consecutive numbers and variables
                    yield self.OPERS["*"][was_num >> 1]
                was_num = 3 - (self.curr == "i")
                yield self.generate_number()
                continue

            # A variable
            if self.curr.isalpha():
                if was_num:
                    # Implicit multiplication - Var Coefficient
                    yield self.OPERS["*"][was_num >> 1]
                yield Token(TokenType.VAR, Var(self.curr))
                was_num = 2

            # An operator
            elif self.curr in "+-":
                yield self.OPERS[self.curr][not was_num]
                was_num = 0
            elif self.curr in self.OPERS:
                if was_num and self.curr in "(√":
                    # Implicit multiplication - Mul
                    yield self.OPERS["*"][1]
                yield self.OPERS[self.curr] if self.curr != "*" else self.OPERS["*"][0]
                was_num = self.curr == ")"

            # An unknown symbol. Terminates immediately
            else:
                yield Token(
                    TokenType.ERROR, SyntaxError(f"unexpected character: '{self.curr}'")
                )
                return
            self.advance()

    def generate_number(self) -> Token:
        """Traverse input string to form a single number"""
        decimals = 0
        if self.curr == "i":
            self.advance()
            return Token(TokenType.CONST, Const(1j))
        number_str = ""
        while self.curr is not None and (self.curr == "." or self.curr.isdigit()):
            if self.curr == ".":
                # Const cannot have multiple decimals
                if decimals:
                    return Token(
                        TokenType.ERROR,
                        SyntaxError("only one decimal point is allowed in number"),
                    )
                decimals = 1
            number_str += self.curr
            self.advance()

        # Const needs atleast one digit
        if number_str == ".":
            return Token(
                TokenType.ERROR, SyntaxError("decimal point needs atlest one digit")
            )
        return Token(TokenType.CONST, Const(number_str))
