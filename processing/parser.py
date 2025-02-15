from typing import Generator, Sequence
from data_types import Number, Variable
from .tokens import Token, TokenType
from .operators import SYMBOLS, Unary, Binary


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
        oper = SYMBOLS.get(oper.type.name)
        raise SyntaxError(f"operator '{oper}' has inadequate operands")

    @staticmethod
    def paren_error() -> None:
        raise SyntaxError("unmatched parenthesis")

    def generate_tuple(self) -> tuple:
        oper = self.curr
        i = 1
        while self.curr and self.curr.type is TokenType.COMMA:
            self.advance()
            i += 1
        res = []
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            if self.curr.type is not TokenType.VAR:
                raise SyntaxError(f"Tuple expected only Variables")
            res.append(self.curr.value)
            if j + 1 < i:
                self.advance()
        return tuple(res)

    def generate_system(self) -> frozenset[Binary]:
        oper = self.curr
        i = 1
        while self.curr and self.curr.type is TokenType.SEMI_COLON:
            self.advance()
            i += 1
        res = []
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            if self.curr.priority != 4:  # A comparison
                raise SyntaxError(f"Systems expected only (in)equalities")
            res.append(self.parse())
            if j + 1 < i:
                self.advance()
        return frozenset(res)

    def parse(self) -> Unary | Binary | Number | Variable | tuple | frozenset | None:
        """Convert from prefix notation to a tree that can be evaluated by the Interpreter"""
        if self.curr is None:
            return
        if self.curr.type in (TokenType.VAR, TokenType.NUMBER):
            return self.curr.value
        if self.curr.type is TokenType.COMMA:
            return self.generate_tuple()
        if self.curr.type is TokenType.SEMI_COLON:
            return self.generate_system()
        oper = self.curr
        self.advance()
        left = self.parse()
        if left is None:
            self.operator_error(oper)
        if oper.type in (TokenType.NEG, TokenType.POS, TokenType.BOOL):
            return Unary(oper, left)
        self.advance()
        right = self.parse()
        if right is None:
            self.operator_error(oper)
        # Check for valid solving syntax
        if oper.type is TokenType.SOLVE:
            if not isinstance(left, (tuple, Variable)):
                raise SyntaxError("can only solve for Variables")
            if not isinstance(right, frozenset) and (
                not isinstance(right, Binary) or right.oper.priority != 4
            ):
                raise SyntaxError("can only solve from an (in)equality")
        # Reject nested (in)equalities
        elif oper.priority == 4:
            if (
                isinstance(left, Binary)
                and left.oper.priority == 4
                or isinstance(right, Binary)
                and right.oper.priority == 4
            ):
                raise SyntaxError("nested (in)equality")
        # Reject operators between terms and non-terms
        elif oper.priority >= 6:
            if (
                isinstance(left, (Binary, Unary))
                and left.oper.priority == 4
                or isinstance(left, (tuple, frozenset))
            ) or (
                isinstance(right, (Binary, Unary))
                and right.oper.priority == 4
                or isinstance(right, (tuple, frozenset))
            ):
                raise TypeError(
                    f"unsupported: {SYMBOLS.get(oper.type.name)} for non-terms"
                )
        return Binary(oper, left, right)

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
            if token.type in (TokenType.NUMBER, TokenType.VAR):
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
        for i in stack:
            if i.type is TokenType.RPAREN:
                self.paren_error()
        yield from reversed(stack)

    def prefix(self, tokens: Sequence[Token]) -> Generator[Token, None, None]:
        """Takes tokens and converts them to prefix notation"""
        return reversed(list(self.postfix(tokens)))
