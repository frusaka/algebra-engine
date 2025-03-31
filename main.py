from timeit import timeit
from processing import AST

while True:
    try:
        if (ast := AST(input("Expression > "))) is not None:
            t = timeit(lambda: ast.eval(), number=1)
            print(ast.eval())
            print(f"Finished in {int(t*1000)}ms")
    except Exception as e:
        # raise e
        print(repr(e).join(("\033[91m", "\033[0m")))
