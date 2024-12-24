from processing import *

# TODO: Watch out for exponents

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
