from typing import Any, Generator, Sequence
from datatypes import Number, Variable
from .tokens import Token, TokenType
from .nodes import SYMBOLS, Sys, Tuple, Unary, Binary
from .lexer import Lexer


class Parser:
    """Takes input tokens and converts it to AST following operator precedence"""

    def __init__(self, tokens: Sequence[Token]) -> None:
        self.tokens = self.prefix(tokens)
        self.advance()

    def advance(self) -> None:
        try:
            self.curr = next(self.tokens)
        except StopIteration:
            self.curr = None

    @staticmethod
    def operator_error(oper) -> None:
        raise SyntaxError(
            f"operator '{SYMBOLS.get(oper.type.name)}' has inadequate operands"
        )

    @staticmethod
    def paren_error() -> None:
        raise SyntaxError("unmatched parenthesis")

    @staticmethod
    def operand_error(oper) -> None:
        raise TypeError(
            f"unsupported: '{SYMBOLS.get(oper.type.name)}' for non-term expressions"
        )

    def generate_iterable(
        self, sep, type, error_msg, parse=True
    ) -> Generator[Any, None, None]:
        oper = self.curr
        i = 1
        while self.curr and self.curr.type is sep:
            self.advance()
            i += 1
        seen = set()
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            if self.curr.type is not type:
                raise SyntaxError(error_msg)
            val = self.parse() if parse else self.curr.value
            if val in seen:
                raise SyntaxError(error_msg)
            seen.add(val)
            yield val
            if j + 1 < i:
                self.advance()

    def parse(self) -> Unary | Binary | Number | Variable | Sys | None:
        """Convert from prefix notation to a tree that can be evaluated by the Interpreter"""
        if self.curr is None:
            return
        if self.curr.type in (TokenType.VAR, TokenType.NUM):
            return self.curr.value
        if self.curr.type is TokenType.TUP:
            return Tuple(
                self.generate_iterable(
                    TokenType.TUP,
                    TokenType.VAR,
                    "tuple expects unique variables only",
                    0,
                )
            )
        if self.curr.type is TokenType.SYS:
            return Sys(
                self.generate_iterable(
                    TokenType.SYS,
                    TokenType.EQ,
                    "system expects unique equations only",
                )
            )
        oper = self.curr
        self.advance()
        left = self.parse()
        p = oper.priority
        if left is None:
            self.operator_error(oper)
        pl = (
            TokenType[
                getattr(left, "oper", None) or left.__class__.__name__[:3].upper()
            ].value
            // 1
        )
        if oper.type in (TokenType.NEG, TokenType.POS):
            if isinstance(left, Sys) or hasattr(left, "oper") and pl < 5:
                self.operand_error(oper)
            return Unary(oper.type.name, left)
        self.advance()
        right = self.parse()
        if right is None:
            self.operator_error(oper)
        pr = (
            TokenType[
                getattr(right, "oper", None) or right.__class__.__name__[:3].upper()
            ].value
            // 1
        )
        # Check for valid solving syntax
        if oper.type is TokenType.SOLVE:
            if not isinstance(left, (Tuple, Variable)):
                raise SyntaxError("can only solve for Variables")
            if right.__class__ is not Sys and (
                not isinstance(right, Binary) or pr != 4
            ):
                raise SyntaxError("can only solve from an (in)equality")
        elif p == 4:
            # Reject nested (in)equalities
            if (
                left.__class__ is Binary
                and pl == 4
                or isinstance(right, Binary)
                and pr == 4
            ):
                raise SyntaxError("nested (in)equality")
            # Reject (in)equality if any of the operands are not term expressions
            if isinstance(left, (Tuple, Sys)) or isinstance(left, (Tuple, Sys)):
                self.operand_error(oper)
        # Reject operators between terms and non-terms
        elif p >= 6:
            if (
                isinstance(left, (Binary, Unary))
                and pl < 5
                or isinstance(left, (Tuple, Sys))
            ) or (
                isinstance(right, (Binary, Unary))
                and pr < 5
                or isinstance(right, (Tuple, Sys))
            ):
                self.operand_error(oper)
        return Binary(oper.type.name, left, right)

    def postfix(self, tokens: Sequence[Token]) -> Generator[Token, None, None]:
        """
        Takes input tokens and converts it to postfix notation.
        properly manages operator precendence
        """
        stack = []
        # NOTE: Reversing the tokens reverses the parentheses
        for token in reversed(list(tokens)):
            # Unkowns or operands
            if token.type is TokenType.ERROR:
                raise token.value
            if token.type in (TokenType.NUM, TokenType.VAR):
                yield token

            # Opening parenthesis
            elif token.type is TokenType.RPAREN:
                stack.append(token)

            # closing parenthesis
            elif token.type is TokenType.LPAREN:
                if not stack:
                    self.paren_error()
                while stack[-1].type != TokenType.RPAREN:
                    yield stack.pop()
                    if not stack:
                        self.paren_error()
                stack.pop()

            # An operator
            else:
                if not stack:
                    self.paren_error()
                if token.type in (TokenType.POW, TokenType.ROOT):
                    while (
                        token.priority <= stack[-1].priority
                        or stack[-1].type is TokenType.NEG
                    ):
                        yield stack.pop()
                else:
                    while token.priority < stack[-1].priority:
                        yield stack.pop()
                stack.append(token)
        for i in reversed(stack):
            if i.type is TokenType.RPAREN:
                self.paren_error()
            yield i

    def prefix(self, tokens: Sequence[Token]) -> Generator[Token, None, None]:
        """Takes tokens and converts them to prefix notation"""
        return reversed(list(self.postfix(tokens)))


def AST(expr: str):
    return Parser(Lexer(expr).generate_tokens()).parse()
