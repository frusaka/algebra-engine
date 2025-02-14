from processing import Interpreter, AST
from data_types import *

proc = Interpreter()

eqns = System(
    {
        proc.eval(AST("x + 2y - z + w + 3v = 10")),
        proc.eval(AST("2x - y + 3z - 2w + v = -5")),
        proc.eval(AST("3x + 4y + 2z + w - v = 12")),
        proc.eval(AST("x - 3y + 4z + 2w + 5v = 7")),
        proc.eval(AST("-2x + y - 3z + w + 4v = -8")),
    }
)
print(eqns[Variable("x"), Variable("y"), Variable("z"), Variable("w"), Variable("v")])
