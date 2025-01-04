from processing.tokens import Token, TokenType
from data_types import Number, Variable


class Lexer:
    OPERS = {
        "=": Token(TokenType.EQ),
        "≠": Token(TokenType.NE),
        ">": Token(TokenType.GT),
        "≥": Token(TokenType.GE),
        "<": Token(TokenType.LT),
        "≤": Token(TokenType.LE),
        "+": (Token(TokenType.ADD), Token(TokenType.POS)),
        "-": (Token(TokenType.SUB), Token(TokenType.NEG)),
        "*": (Token(TokenType.MUL), Token(TokenType.MUL, iscoef=True)),
        "/": Token(TokenType.TRUEDIV),
        "^": Token(TokenType.POW),
        "√": Token(TokenType.ROOT),
        "(": Token(TokenType.LPAREN),
        ")": Token(TokenType.RPAREN),
    }

    def __init__(self, expr: str):
        self.expr = iter(expr.join("()"))
        self.advance()

    def advance(self):
        try:
            self.curr = next(self.expr)
        except StopIteration:
            self.curr = None

    def generate_tokens(self):
        was_num = 0
        while self.curr is not None:
            if self.curr in " \n\t":
                self.advance()
                continue
            if self.curr == "." or self.curr.isdigit():
                # Can be toggled off to experiment with other notations (prefix & postfix)
                if was_num:
                    if was_num == 3:
                        yield Token(
                            TokenType.ERROR, SyntaxError("No operator between numbers")
                        )
                        return
                    # Implicit multiplication - Parenthesis or consecutive numbers numbers
                    yield self.OPERS["*"][was_num >> 1]
                yield self.generate_number()
                was_num = 3
                continue
            if self.curr.isalpha():
                if was_num:
                    # Implicit multiplication - Variable Coefficient
                    yield self.OPERS["*"][was_num >> 1]
                yield Token(TokenType.VAR, Variable(self.curr))
                was_num = 2
            elif self.curr in "+-":
                yield self.OPERS[self.curr][not was_num]
                was_num = 0
            elif self.curr in self.OPERS:
                if was_num and self.curr == "(":
                    # Implicit multiplication - Product
                    yield self.OPERS["*"][1]
                yield self.OPERS[self.curr] if self.curr != "*" else self.OPERS["*"][0]
                was_num = self.curr == ")"
            else:
                yield Token(
                    TokenType.ERROR, SyntaxError(f"unexpected character: '{self.curr}'")
                )
                return
            self.advance()

    def generate_number(self):
        decimals = 0
        number_str = ""
        while self.curr is not None and (self.curr == "." or self.curr.isdigit()):
            if self.curr == ".":
                if decimals:
                    return Token(
                        TokenType.ERROR,
                        SyntaxError("only one decimal point is allowed in number"),
                    )
                decimals = 1
            number_str += self.curr
            self.advance()
        if number_str == ".":
            return Token(
                TokenType.ERROR, SyntaxError("decimal point needs atlest one digit")
            )
        return Token(TokenType.NUMBER, Number(number_str))
