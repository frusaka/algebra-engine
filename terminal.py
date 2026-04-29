from rich import print

from utils import steps
from parsing import parser

from parsing.lexer import Lexer


print("[bold magenta]Algebra Engine[/bold magenta]")
print("Type an expression to evaluate it, or press Ctrl+C to exit.")

steps.set_verbosity(True)


while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).tokenize()).parse()
        print(steps.explain(inp))
    except Exception as e:
        # raise
        print(repr(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
