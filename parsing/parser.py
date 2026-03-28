from typing import Generator, Iterable
from solving.comparison import Comparison, CompRel
from datatypes.base import Node
from solving.system import System
from parsing import operators
from .tokens import FUNCTIONS, Token, TokenType
from .lexer import Lexer
from utils.constants import SYMBOLS


class Parser:
    """Takes input tokens and converts it to AST following operator precedence"""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.tokens = self.prefix(tokens)
        self.advance()

    def advance(self) -> None:
        try:
            self.curr = next(self.tokens)
        except StopIteration:
            self.curr = None

    @classmethod
    def postfix(cls, tokens: Iterable[Token]) -> Generator[TokenType, None, None]:
        """
        Takes input tokens and converts it to postfix notation.
        properly manages operator precendence
        """
        stack = []
        # NOTE: Reversing the tokens reverses the parentheses
        for idx, token in enumerate(
            reversed(
                tks := [Token(TokenType.LPAREN), *tokens, Token(TokenType.RPAREN)]
            ),
            1,
        ):
            # Unkowns or operands
            if token.type is TokenType.ERROR:
                raise token.value
            if token.type in (TokenType.CONST, TokenType.VAR):
                yield token.value

            # Opening parenthesis
            elif token.type in (TokenType.RPAREN, TokenType.RBRACK):
                stack.append(token)

            # closing parenthesis
            elif token.type in (TokenType.LPAREN, TokenType.LBRACK):
                if not stack:
                    cls.paren_error(token.type)
                while stack[-1].type not in (
                    TokenType.RPAREN,
                    TokenType.RBRACK,
                ):
                    yield stack.pop().type
                    if not stack:
                        cls.paren_error(token.type)
                if stack[-1].type.name != "R" + token.type.name[1:]:
                    if len(stack) > 1:
                        if idx < len(tks):
                            cls.paren_error(stack[-1].type, token.type)
                        cls.paren_error(stack[-1].type)
                    cls.paren_error(token.type)
                stack.pop()
                if token.type is TokenType.LBRACK:
                    yield token.type

            # An operator
            else:
                if not stack:
                    cls.paren_error(TokenType.LPAREN)
                if token.type is TokenType.POW:
                    while (
                        token.priority <= stack[-1].priority
                        or stack[-1].type.is_unary()
                    ):
                        yield stack.pop().type
                else:
                    while (
                        token.priority < stack[-1].priority or stack[-1].type.is_unary()
                    ):
                        yield stack.pop().type
                stack.append(token)

        for i in reversed(stack):
            if i.type in (TokenType.RPAREN, TokenType.RBRACK):
                cls.paren_error(i.type)
            yield i.type

    @classmethod
    def prefix(cls, tokens: Iterable[Token]) -> Generator[TokenType, None, None]:
        """Takes tokens and converts them to prefix notation"""
        return reversed(list(cls.postfix(tokens)))

    @staticmethod
    def operator_error(oper) -> None:
        raise SyntaxError(
            f"operator '{SYMBOLS.get(oper.name)}' has inadequate operands"
        )

    @staticmethod
    def paren_error(opening: TokenType, closing: TokenType = None) -> None:
        opening = SYMBOLS.get(opening.name)
        if not closing:
            if opening in "])":
                raise SyntaxError(f"unmatched '{opening}'")
            raise SyntaxError(f"'{opening}' was never closed")
        closing = SYMBOLS.get(closing.name)
        raise SyntaxError(
            f"closing parenthesis '{opening}' does not match opening parenthesis '{closing}'"
        )

    @staticmethod
    def brack_error() -> None:
        raise SyntaxError("unmatched brackets")

    @staticmethod
    def operand_error(oper) -> None:
        raise TypeError(
            f"unsupported: '{SYMBOLS.get(oper.name)}' for non-term expressions"
        )

    def generate_iterable(self) -> Generator:
        oper = self.curr
        i = 1
        while self.curr and self.curr is TokenType.COMMA:
            self.advance()
            i += 1
        seen = set()
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            val = self._parse()
            seen.add(val)
            yield val
            if j + 1 < i:
                self.advance()

    def generate_system(self, vals: Iterable) -> Generator[Comparison, None, None]:
        error_msg = "system expects unique equations only"
        if not hasattr(vals, "__iter__"):
            raise ValueError(error_msg)
        seen = set()
        for i in vals:
            if i.__class__ is not Comparison or i.rel is not CompRel.EQ or i in seen:
                raise ValueError(error_msg)
            seen.add(i)
            yield i

    def _parse(self):
        if self.curr is None:
            return
        if not isinstance(self.curr, TokenType):
            return self.curr
        if self.curr is TokenType.COMMA:
            return tuple(self.generate_iterable())
        oper = self.curr
        self.advance()
        left = self._parse()
        if left is None:
            self.operator_error(oper)
        if oper is TokenType.LBRACK:
            return operators.System(self.generate_system(left))
        if oper.is_unary():
            if isinstance(left, tuple):
                return getattr(operators, oper.name.lower())(*left)
            if not isinstance(left, Node) and oper.value >= 6:
                self.operand_error(oper)
            return getattr(operators, oper.name.lower())(left)
        self.advance()
        right = self._parse()

        if right is None:
            self.operator_error(oper)
        if oper.value // 1 == 4:
            # Reject nested (in)equalities
            if isinstance(left, Comparison) or isinstance(right, Comparison):
                raise SyntaxError("nested (in)equality")
            # Reject (in)equality if any of the operands are not term expressions
            if not isinstance(left, Node) or not isinstance(right, Node):
                self.operand_error(oper)
        # Reject operators between terms and non-terms
        elif (
            oper.value >= 6
            and not isinstance(left, Node)
            or not isinstance(right, Node)
        ):
            self.operand_error(oper)
        return getattr(operators, oper.name.lower())(left, right)

    def parse(self, autosolve: bool = True) -> Node | Comparison | System | None:
        op = self.curr
        res = self._parse()
        self.advance()
        if self.curr:
            raise SyntaxError("Malformed expression")
        if (
            isinstance(res, (System, Comparison))
            and autosolve
            and op.name not in FUNCTIONS
        ):
            return operators.solve(res)
        return res


def eval(expr: str, autosolve: bool = True) -> Node:
    return Parser(Lexer(expr).tokenize()).parse(autosolve)


def AST(expr: str) -> tuple[Node]:
    return tuple(Parser.prefix(Lexer(expr).tokenize()))
