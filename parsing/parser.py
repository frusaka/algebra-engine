import inspect
import types
from typing import Generator, Iterable, get_origin, get_args, Union

from solving.comparison import Comparison
from datatypes.base import Expr
from solving.system import System
from parsing import operators
from .tokens import FUNCTIONS, Token, TokenType
from .lexer import Lexer
from utils.constants import SYMBOLS


class Function:
    def __init__(self, func: str, *args):
        self.func = func
        self.args = args
        self.return_type = inspect.signature(getattr(operators, func)).return_annotation
        if isinstance(self.return_type, str):
            self.return_type = eval(self.return_type)
        self.validate()

    def __repr__(self):
        return f'Function("{self.func}", {",".join(map(repr, self.args))})'

    def __hash__(self):
        return hash((type(self), self.func, self.args))

    def __eq__(self, value):
        if type(value) is not type(self):
            return False
        return (self.func, self.args) == (value.func, value.args)

    def __call__(self):
        return getattr(operators, self.func)(
            *(
                (
                    (arg if arg is not TokenType.NaN else None)
                    if arg.__class__ is not self.__class__
                    else arg()
                )
                for arg in self.args
            )
        )

    def validate(self):
        def check_type(value, expected):
            origin = get_origin(expected)
            # Plain type
            if origin is None:
                if isinstance(expected, str):
                    return issubclass(value, eval(expected))
                return issubclass(value, expected)

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

        sig = inspect.signature(getattr(operators, self.func))
        sig_str = self.func + ", ".join(
            (
                (k if not v.kind == inspect.Parameter.VAR_POSITIONAL else "*" + k)
                + ": "
                + format_type(v.annotation)
            )
            for k, v in sig.parameters.items()
        ).join("()")
        args = []
        for arg in self.args:
            if arg is None:
                continue
            if arg is TokenType.NaN:
                args.append(type(None))
            elif isinstance(arg, Function):
                args.append(arg.return_type)
            else:
                args.append(type(arg))

        try:
            bound = sig.bind(*args)
        except TypeError as e:
            raise SyntaxError(f"{sig_str} {e}")
        if sig.parameters and not any(args):
            raise SyntaxError(f"{sig_str} needs atleast one value")
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            param = sig.parameters[name]
            expected = param.annotation
            exp = format_type(expected)

            if expected is inspect._empty:
                continue
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                for item in value:
                    if not check_type(item, expected):
                        raise TypeError(
                            f"Argument mismatch: {sig_str} arguments '{name}' must be of type "
                            f"{exp}, got {item.__name__}"
                        )
            elif not check_type(value, expected):
                raise TypeError(
                    f"Argument mismatch: {sig_str} argument '{name}' must be of type {exp}, got {value.__name__}"
                )
        return True


class Parser:
    """Takes input tokens and converts it to AST following operator precedence"""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.tokens = reversed(list(self.postfix(tokens)))
        self.empty = not tokens
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

    def generate_iterable(self) -> Generator:
        oper = self.curr
        i = 1
        while self.curr and self.curr is TokenType.COMMA:
            self.advance()
            i += 1
        for j in range(i):
            if self.curr is None:
                self.operator_error(oper)
            val = self._parse()
            yield val
            if j + 1 < i:
                self.advance()

    def _parse(self):
        if self.curr is None:
            return
        if not isinstance(self.curr, TokenType) or self.curr is TokenType.NaN:
            return self.curr
        if self.curr is TokenType.COMMA:
            return self.generate_iterable()
        oper = self.curr
        self.advance()
        left = self._parse()
        func = oper.name.lower()
        if oper.is_unary():
            if oper is TokenType.LBRACK:
                func = "system"
            if inspect.isgenerator(left):
                return Function(func, *left)
            if oper is TokenType.SQRT:
                return Function(func, TokenType.NaN, left)
            return Function(func, left)
        self.advance()
        right = self._parse()
        return Function(func, left, right)

    def parse(self, autosolve: bool = True) -> Expr | Comparison | System | None:
        op = self.curr
        res = self._parse()
        self.advance()
        if self.curr:
            raise SyntaxError("Malformed expression")
        if res is None and not self.empty:
            raise SyntaxError("Empty Expression")
        if isinstance(res, Function):
            res = res()
        if (
            isinstance(res, (System, Comparison))
            and autosolve
            and op.name not in FUNCTIONS
        ):
            return operators.solve(res)
        return res


def parse(expr: str, autosolve: bool = True) -> Expr:
    return Parser(Lexer(expr).tokenize()).parse(autosolve)


def AST(expr: str):
    return Parser(Lexer(expr).tokenize())._parse()
