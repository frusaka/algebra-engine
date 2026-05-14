from rich import print

from utils import steps
from parsing import parser


print("[bold magenta]Algebra Engine[/bold magenta]")
print(
    "[italic]Type an expression to evaluate it, or press [purple]Ctrl+C[/purple] to exit.[/italic]"
)

steps.set_verbosity(True)


while True:
    print("[bold purple]>>>[/bold purple]", end=" ")
    try:
        inp = parser.parse(input(""))
        print(steps.explain(inp, maxdepth=1, adaptive=True))
    except Exception as e:
        # raise e
        print(steps.explain(e))
    except KeyboardInterrupt:
        print("\nExiting...")
        break
