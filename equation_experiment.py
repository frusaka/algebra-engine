from data_types import Variable, Equation
from processing import Interpreter, AST

interpretter = Interpreter()
while True:
    try:
        left, right = input("Equation> ").split("=")
        left = interpretter.eval(AST(left))
        right = interpretter.eval(AST(right))
        Equation(left, right)[Variable(input("Variable> "))]
    except Exception as e:
        print(repr(e).join(("\033[91m", "\033[0m")))
