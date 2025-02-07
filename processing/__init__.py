from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .tokens import Token, TokenType
from .operators import *


def AST(expr: str):
    return Parser(Lexer(expr).generate_tokens()).parse()
