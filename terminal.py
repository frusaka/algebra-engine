from rich.console import Console

from datatypes.base import Node
from solving.eval_trace import ETSteps
from parsing import parser

from parsing.lexer import Lexer

print = Console().print

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).generate_tokens())
        res = inp.parse()
        if res is None:
            continue
        if isinstance(res, Node):
            res = res.simplify()
        if ETSteps.data:
            print(ETSteps.torich())
        print(res)
    except Exception as e:
        if ETSteps.data:
            print(ETSteps.torich())
        # raise
        print(repr(e))
    ETSteps.clear()
