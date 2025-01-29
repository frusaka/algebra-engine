from processing import Interpreter, AST

# TODO: Refactor and Document the project

processor = Interpreter()
while True:
    try:
        if ast := AST(input("Expression > ")):
            print(processor.eval(ast))
    except Exception as e:
        # raise e
        print(repr(e).join(("\033[91m", "\033[0m")))
