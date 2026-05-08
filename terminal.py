from rich import print

from utils import steps
from parsing import parser

from parsing.lexer import Lexer

print("[bold magenta]Algebra Engine[/bold magenta]")
print(
    "[italic]Type an expression to evaluate it, or press [purple]Ctrl+C[/purple] to exit.[/italic]"
)

steps.set_verbosity(True)


while True:
    print("[bold purple]>>>[/bold purple]", end=" ")
    try:
        inp = parser.Parser(Lexer(input("")).tokenize()).parse()
        print(steps.explain(inp, maxdepth=None))
    except Exception as e:
        # raise e
        print(steps.explain(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
