from .lexer import Lexer
from .parser_ import Parser
from .interpreter import Interpreter
from .tokens import Token, TokenType


def AST(expr: str):
    return Parser(Lexer(expr).generate_tokens()).parse()
