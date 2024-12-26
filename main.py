from processing import *

# TODO: Make Polynomial divisions robust
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
        print(repr(e).join(("\033[91m", "\033[0m")))
