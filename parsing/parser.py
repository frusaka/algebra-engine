import inspect
import types
from typing import Generator, Iterable, get_origin, get_args, Union

from solving.comparison import Comparison, CompRel
from datatypes.base import Node
from solving.system import System
from parsing import operators
from .tokens import FUNCTIONS, Token, TokenType
from .lexer import Lexer
from utils.constants import SYMBOLS

_eval = eval


def validate(func, *args, call=True):
    def check_type(value, expected):
        origin = get_origin(expected)
        # Plain type
        if origin is None:
            if isinstance(expected, str):
                return isinstance(value, _eval(expected))
            return isinstance(value, expected)

        # Union (typing.Union or | syntax)
        if origin is Union or origin is types.UnionType:
            return any(check_type(value, t) for t in get_args(expected))

        return True

    def format_type(t):
        if t is None:
            return "None"

        origin = get_origin(t)

        # Simple types (int, Var, etc.)
        if origin is None:
            if hasattr(t, "__name__"):
                return t.__name__
            return str(t).replace("<class '", "").replace("'>", "")

        # Handle Union (Union[...] or | syntax)
        if origin is Union or origin is types.UnionType:
            return " | ".join(format_type(arg) for arg in get_args(t))

        # Handle generics like list[int], dict[str, int]
        args = ", ".join(format_type(arg) for arg in get_args(t))

        if hasattr(origin, "__name__"):
            return f"{origin.__name__}[{args}]"

        return str(t)

    sig = inspect.signature(func)
    args = tuple(i if i is not TokenType.NaN else None for i in args if i is not None)
    sig_str = func.__name__ + ", ".join(
        (
            (k if not v.kind == inspect.Parameter.VAR_POSITIONAL else "*" + k)
            + ": "
            + format_type(v.annotation)
        )
        for k, v in sig.parameters.items()
    ).join("()")
    sig_str = sig_str.replace("Node", "Term").replace("node", "term")
    try:
        bound = sig.bind(*args)
    except TypeError as e:
        raise SyntaxError(f"{sig_str} {e}".replace("node", "term"))
    bound.apply_defaults()
    for name, value in bound.arguments.items():
        param = sig.parameters[name]
        expected = param.annotation
        exp = format_type(expected).replace("Node", "Term")

        if expected is inspect._empty:
            continue
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            for item in value:
                if not check_type(item, expected):
                    got = item.__class__.__name__ if item is not Node else "Term"
                    raise TypeError(
                        f"Argument mismatch: {sig_str} arguments '{name}' must be of type"
                        f"{exp}, got {got}"
                    )
        elif not check_type(value, expected):
            got = value.__class__.__name__ if value is not Node else "Term"
            raise TypeError(
                f"Argument mismatch: {sig_str} argument '{name}' must be of type {exp}, got {got}"
            )
    if call:
        return func(*args)
    return True


class Parser:
    """Takes input tokens and converts it to AST following operator precedence"""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.tokens = reversed(list(self.postfix(tokens)))
        self.empty = not tokens

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
            # None
            elif token.type is TokenType.NaN:
                yield token.type
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
        if not isinstance(self.curr, TokenType) or self.curr is TokenType.NaN:
            return self.curr
        if self.curr is TokenType.COMMA:
            return tuple(self.generate_iterable())
        oper = self.curr
        self.advance()
        left = self._parse()
        if oper is TokenType.LBRACK:
            return operators.System(self.generate_system(left))
        func = getattr(operators, oper.name.lower())
        if oper.is_unary():
            if isinstance(left, tuple):
                return validate(func, *left)
            if oper is TokenType.SQRT:
                return validate(func, TokenType.NaN, left)
            return validate(func, left)
        self.advance()
        right = self._parse()
        return validate(func, left, right)

    def parse(self, autosolve: bool = True) -> Node | Comparison | System | None:
        self.advance()
        op = self.curr
        res = self._parse()
        self.advance()
        if self.curr:
            raise SyntaxError("Malformed expression")
        if res is None and not self.empty:
            raise SyntaxError("Empty Expression")
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
    return tuple(Parser(Lexer(expr).tokenize()).tokens)
