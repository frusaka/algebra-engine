from rich import print

from datatypes import *

from step_tracking import explain, set_verbosity
from step_tracking.eval_trace import _steps
from parsing import parser

from parsing.lexer import Lexer


print("[bold magenta]Algebra Engine[/bold magenta]")
print("Type an expression to evaluate it, or press Ctrl+C to exit.")

set_verbosity(True)

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).tokenize()).parse()
        print(_steps)
        print(explain(inp))
    except Exception as e:
        raise
        print(repr(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
