import cProfile
import pstats
from rich.console import Console
from solving.eval_trace import ETSteps
from parsing import parser

from parsing.lexer import Lexer

print = Console().print

print("[bold magenta]Algebra Engine[/bold magenta]")
print("Type an expression to evaluate it, or press Ctrl+C to exit.")

profiler = cProfile.Profile()

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).tokenize())

        profiler.enable()
        res = inp.parse()
        profiler.disable()
        if res is None:
            continue
        if ETSteps.data:
            print(ETSteps.torich())
        print(res)

        # Print profiling stats
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumtime")
        print("\n[bold yellow]Profiling Results:[/bold yellow]")
        stats.print_stats(20)
        profiler.clear()
    except Exception as e:
        profiler.disable()
        if ETSteps.data:
            print(ETSteps.torich())
        # raise
        print(repr(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    ETSteps.clear()
