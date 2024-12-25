from processing import *

# TODO: Implement special case for Polynomial divisions
# TODO: Generalize base cases for operations on non-like Terms

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
        print("\033[91m" + str(e) + "\033[0m")
