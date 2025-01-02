from processing import AST
from data_types import Number, Term


def test_simplify_constants(interpreter):
    assert interpreter.eval(AST("10 + 5 - 3")) == Term(Number(12))
    assert interpreter.eval(AST("20 - 4 + 2")) == Term(Number(18))
    assert interpreter.eval(AST("2 * 3 + 4")) == Term(Number(10))
    assert interpreter.eval(AST("10 / 2 + 5")) == Term(Number(10))
    assert interpreter.eval(AST("2^3 + 1")) == Term(Number(9))
    assert interpreter.eval(AST("(2 + 3) * 4")) == Term(Number(20))
    assert interpreter.eval(AST("10 / (2 + 3)")) == Term(Number(2))
    assert interpreter.eval(AST("2 * (3 + 4)")) == Term(Number(14))
    assert interpreter.eval(AST("(2 + 3) * (4 + 1)")) == Term(Number(25))
