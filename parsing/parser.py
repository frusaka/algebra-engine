from dataclasses import dataclass
from itertools import chain
from typing import Generator, Iterable, Sequence
from solving.comparison import Comparison
from datatypes.nodes import Const, Var
from datatypes.base import Collection, Node
from solving.system import System
from parsing import operators
from .tokens import Token, TokenType
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

    @staticmethod
    def operator_error(oper) -> None:
        raise SyntaxError(
            f"operator '{SYMBOLS.get(oper.name)}' has inadequate operands"
        )

    @staticmethod
    def paren_error() -> None:
        raise SyntaxError("unmatched parenthesis")

    @staticmethod
    def operand_error(oper) -> None:
        raise TypeError(
            f"unsupported: '{SYMBOLS.get(oper.name)}' for non-term expressions"
        )

    def generate_system(self) -> Generator[Comparison, None, None]:
        oper = self.curr
        error_msg = "system expects unique equations only"
        i = 1
        while self.curr and self.curr is TokenType.COMMA:
            self.advance()
            i += 1
        seen = set()
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            if self.curr is not TokenType.EQ:
                raise SyntaxError(error_msg)
            val = self._parse()
            if val in seen:
                raise SyntaxError(error_msg)
            seen.add(val)
            yield val
            if j + 1 < i:
                self.advance()

    def _parse(self):
        if self.curr is None:
            return
        if not isinstance(self.curr, TokenType):
            return self.curr
        if self.curr is TokenType.COMMA:
            return System(self.generate_system())
        oper = self.curr
        self.advance()
        left = self._parse()
        if left is None:
            self.operator_error(oper)
        if oper.is_unary():
            if not isinstance(left, Node) and oper.value >= 6:
                self.operand_error(oper)
            return getattr(operators, oper.name.lower())(left)
        self.advance()
        right = self._parse()
        if right is None:
            self.operator_error(oper)
        # Check for valid solving syntax
        if oper is TokenType.SOLVE:
            if not isinstance(left, Var):
                raise SyntaxError("can only solve for Variables")
            if not isinstance(right, Comparison):
                raise SyntaxError("can only solve from an (in)equality")
            return (left, right)
        elif oper.value // 1 == 4:
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

    def parse(self) -> Node | Comparison | System | None:
        res = self._parse()
        self.advance()
        if self.curr:
            raise SyntaxError("Malformed expression")
        # From solving
        if type(res) is tuple:
            return operators.solve(*res)
        if not isinstance(res, (System, Comparison)):
            return res
        # Automatically solve systems of equations or single-variable Comparisons
        vars = set(filter(str.isalpha, str(res))) - {"i"}
        if not vars:
            return res.is_close(1e-3)
        if res.__class__ is Comparison:
            if len(vars) == 1:
                return operators.solve(Var(vars.pop()), res)
            return res
        return operators.solve(tuple(map(Var, sorted(vars))), res)

    @classmethod
    def postfix(cls, tokens: Iterable[Token]) -> Generator[TokenType, None, None]:
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
            if token.type in (TokenType.CONST, TokenType.VAR):
                yield token.value

            # Opening parenthesis
            elif token.type is TokenType.RPAREN:
                stack.append(token)

            # closing parenthesis
            elif token.type is TokenType.LPAREN:
                if not stack:
                    cls.paren_error()
                while stack[-1].type != TokenType.RPAREN:
                    yield stack.pop().type
                    if not stack:
                        cls.paren_error()
                stack.pop()

            # An operator
            else:
                if not stack:
                    cls.paren_error()

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
            if i.type is TokenType.RPAREN:
                cls.paren_error()
            yield i.type

    @classmethod
    def prefix(cls, tokens: Iterable[Token]) -> Generator[TokenType, None, None]:
        """Takes tokens and converts them to prefix notation"""
        return reversed(list(cls.postfix(tokens)))


def eval(expr: str) -> Node:
    return Parser(Lexer(expr).generate_tokens()).parse()


def AST(expr: str) -> tuple[Node]:
    return tuple(Parser.prefix(Lexer(expr).generate_tokens()))
