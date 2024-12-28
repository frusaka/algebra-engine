from processing import *

# TODO: Refactor and Document the project
# NOTE: For polynomials, a * b^-1 does not yield the same result as a/b

comp = Interpreter()
while True:
    try:
        prefix = list(Lexer(input("Expression > ")).prefix())
        tree = Parser(prefix).parse()
        # print(prefix)
        print(tree)
        print(comp.eval(tree))
    except Exception as e:
        # raise e
        print(repr(e).join(("\033[91m", "\033[0m")))
