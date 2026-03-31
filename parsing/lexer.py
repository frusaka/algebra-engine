from pylatexenc.latexwalker import *


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
        "+": Token(TokenType.POS),
        "-": Token(TokenType.NEG),
        "*": Token(TokenType.MUL),
        "/": Token(TokenType.DIV),
        "^": Token(TokenType.POW),
        "~": Token(TokenType.APPROX),
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
        while self.curr is not None:
            if self.curr in " \n\t":  # Ignore spaces
                self.advance()
                continue

            if self.curr in "i." or self.curr.isdigit():
                yield self.generate_number()
                continue

            # A variable or function
            if self.curr.isalpha():
                tk = self.generate_identifier()
                if tk.__class__ is str:
                    for i in tk:
                        yield Token(TokenType.VAR, Var(i))
                else:
                    yield tk
                continue

            # An operator
            elif self.curr in self.OPERS:
                yield self.OPERS[self.curr]
            # An unknown symbol. Terminates immediately
            else:
                yield Token(
                    TokenType.ERROR, SyntaxError(f"unexpected character: '{self.curr}'")
                )
                return
            self.advance()

    def tokenize(self) -> Generator[Token, None, None]:
        def dfs(node):
            if node is None:
                yield Token(TokenType.NaN)
            elif node.__class__ is LatexCharsNode:
                yield from self.__class__(node.chars).generate_tokens()
            elif node.__class__ is LatexGroupNode:
                if (
                    len(node.nodelist) == 1
                    and node.nodelist[0].__class__ is not LatexCharsNode
                ):
                    yield from dfs(node.nodelist[0])
                else:
                    yield Token(TokenType.LPAREN)
                    for n in node.nodelist:
                        yield from dfs(n)
                    yield Token(TokenType.RPAREN)
            elif node.__class__ is LatexMacroNode:
                if node.macroname in ("left", "right", "operatorname"):
                    return
                if node.macroname == "mathrm":
                    for n in node.nodeargd.argnlist[0].nodelist:
                        yield from dfs(n)
                    return
                if not TokenType.__members__.get(node.macroname.upper()):
                    yield Token(
                        TokenType.ERROR,
                        SyntaxError(f"unknown operator: '{node.macroname}'"),
                    )
                    return
                yield Token(TokenType[node.macroname.upper()])
                if not node.nodeargd or not node.nodeargd.argnlist:
                    return
                nodes = node.nodeargd.argnlist
                if len(nodes) > 1:
                    yield Token(TokenType.LPAREN)
                for idx, n in enumerate(nodes):
                    yield from dfs(n)
                    if idx + 1 < len(nodes):
                        yield Token(TokenType.COMMA)
                if len(nodes) > 1:
                    yield Token(TokenType.RPAREN)
            elif node.__class__ is LatexMathNode:
                for i in node.nodelist:
                    yield from dfs(i)
            elif node.__class__ is LatexSpecialsNode:
                yield from self.__class__(node.specials_chars).generate_tokens()
            else:
                yield Token(
                    TokenType.ERROR,
                    SyntaxError(f"unexpected latex node: {node.__class__.__name__}"),
                )

        was_num = 0
        num_dict = {TokenType.CONST: 3, TokenType.VAR: 2, TokenType.RPAREN: 1}
        for i in LatexWalker(self.expr).get_latex_nodes()[0]:
            for j in dfs(i):
                if j.type is TokenType.ERROR:
                    yield j
                    return
                if was_num:
                    if j.type is TokenType.POS:
                        was_num = 0
                        yield Token(TokenType.ADD)
                        continue
                    if j.type is TokenType.NEG:
                        was_num = 0
                        yield Token(TokenType.SUB)
                        continue
                    if j.type in (
                        TokenType.LPAREN,
                        TokenType.CONST,
                        TokenType.VAR,
                    ):
                        if (
                            j.type is TokenType.CONST
                            and not j.value.numerator.imag
                            and was_num > 1
                        ):
                            yield Token(
                                TokenType.ERROR,
                                SyntaxError(
                                    "no operator between numbers"
                                    if was_num == 3
                                    else "variable preceeding digit"
                                ),
                            )
                            return
                        was_num = 0
                        yield Token(TokenType.MUL, iscoef=j.type is TokenType.VAR)
                    if j.type.name in FUNCTIONS:
                        yield Token(TokenType.MUL)
                yield j
                was_num = num_dict.get(j.type, 0)
