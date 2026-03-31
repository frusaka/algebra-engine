from rich.console import Console
from solving.eval_trace import ETSteps
from parsing import parser

from parsing.lexer import Lexer

print = Console().print

print("[bold magenta]Algebra Engine[/bold magenta]")
print("Type an expression to evaluate it, or press Ctrl+C to exit.")

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).tokenize())
        res = inp.parse()
        if res is None:
            continue
        if ETSteps.data:
            print(ETSteps.torich())
        print(res)
    except Exception as e:
        if ETSteps.data:
            print(ETSteps.torich())
        # raise
        print(repr(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    ETSteps.clear()
