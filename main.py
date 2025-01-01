from processing import Interpreter, AST

# TODO: Refactor and Document the project
# NOTE: For polynomials, a * b^-1 does not yield the same result as a/b

comp = Interpreter()
while True:
    try:
        if ast := AST(input("Expression > ")):
            print(comp.eval(ast))
    except Exception as e:
        # raise e
        print(repr(e).join(("\033[91m", "\033[0m")))
