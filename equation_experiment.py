from data_types import Variable, Equation
from processing import Interpreter, AST

interpretter = Interpreter()
eq = Equation(interpretter.eval(AST("2x+3y")), interpretter.eval(AST("5-3x")))
print(eq)
print(eq[Variable("x")])
