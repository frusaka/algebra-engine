from rich import print

from utils.eval_trace import explain, set_verbosity
from parsing import parser

from parsing.lexer import Lexer


print("[bold magenta]Algebra Engine[/bold magenta]")
print("Type an expression to evaluate it, or press Ctrl+C to exit.")

set_verbosity(True)

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).tokenize()).parse()
        print(explain(inp))
    except Exception as e:
        # raise
        print(repr(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
