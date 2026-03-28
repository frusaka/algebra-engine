from pylatexenc.latexwalker import (
    LatexWalker,
    LatexGroupNode,
    LatexCharsNode,
    LatexMacroNode,
)


from fractions import Fraction
from typing import Generator
from parsing.tokens import Token, TokenType, FUNCTIONS
from datatypes.nodes import Const, Var


class Lexer:
    """Takes input string and Tokenizes it"""

    OPERS = {
        **dict((i.lower, TokenType[i]) for i in FUNCTIONS),
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
        "[": Token(TokenType.LBRACK),
        "]": Token(TokenType.RBRACK),
    }

    def __init__(self, expr: str) -> None:
        self.expr = expr.replace(">=", "≥").replace("<=", "≤")

    def advance(self) -> None:
        try:
            self.curr = next(self.expr)
        except StopIteration:
            self.curr = None

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
        val = Fraction(number_str).limit_denominator()
        return Token(TokenType.CONST, Const(val.numerator, val.denominator))

    def generate_identifier(self) -> Token | str:
        var = ""
        while self.curr is not None and self.curr.isalpha():
            var += self.curr
            self.advance()
        if var.upper() in FUNCTIONS:
            return Token(TokenType[var.upper()])
        return var

    def generate_tokens(self) -> Generator[Token, None, None]:
        """Generate tokens based on input string"""
        self.expr = iter(self.expr)
        self.advance()
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

            # A variable or function
            if self.curr.isalpha():
                tk = self.generate_identifier()
                if tk.__class__ is str:
                    for i in tk:
                        if was_num:
                            # Implicit multiplication - Var Coefficient
                            yield self.OPERS["*"][was_num >> 1]
                        yield Token(TokenType.VAR, Var(i))
                        was_num = 2
                else:
                    was_num = 0
                    yield tk
                continue

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

    def tokenize(self) -> Generator[Token, None, None]:
        def dfs(node):
            if node.__class__ is LatexCharsNode:
                yield from self.__class__(node.chars).generate_tokens()
            elif node.__class__ is LatexGroupNode:
                yield Token(TokenType.LPAREN)
                for n in node.nodelist:
                    yield from dfs(n)
                yield Token(TokenType.RPAREN)
                return
            elif node.__class__ is LatexMacroNode:
                if node.macroname in ("left", "right"):
                    return
                yield Token(TokenType[node.macroname.upper()])
                if node.nodeargd.argnlist:
                    for n in node.nodeargd.argnlist:
                        yield from dfs(n)

        for n in LatexWalker(self.expr, tolerant_parsing=False).get_latex_nodes()[0]:
            yield from dfs(n)
