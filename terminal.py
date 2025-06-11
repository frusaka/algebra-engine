from processing import Interpreter, AST
from datatypes import steps

processor = Interpreter()

while True:
    try:
        if (ast := AST(input("Expression > "))) is not None:
            res = processor.eval(ast)
            if steps:
                print(steps)
            print(res)
    except Exception as e:
        # raise e
        print(repr(e).join(("\033[91m", "\033[0m")))
