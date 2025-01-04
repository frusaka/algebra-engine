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


def test_add_complex(interpreter):
    assert interpreter.eval(AST("(3+4i) + (1+2i)")) == Term(Number(4, 6))
    assert interpreter.eval(AST("(5+0i) + (0+3i)")) == Term(Number(5, 3))
    assert interpreter.eval(AST("(-2-3i) + (4-5i)")) == Term(Number(2, -8))
    assert interpreter.eval(AST("(0+0i) + (0+0i)")) == Term(Number())
    assert interpreter.eval(AST("(6+2i) + (-6+6i)")) == Term(Number(imag=8))


def test_subtract_complex(interpreter):
    assert interpreter.eval(AST("(6+5i) - (4+3i)")) == Term(Number(2, 2))
    assert interpreter.eval(AST("(3+7i) - (3+7i)")) == Term(Number())
    assert interpreter.eval(AST("0 - (5+6i)")) == Term(Number(-5, -6))
    assert interpreter.eval(AST("(-1+4i) - (2-2i)")) == Term(Number(-3, 6))
    assert interpreter.eval(AST("(12+3i) - (12-1i)")) == Term(Number(imag=4))


def test_multiply_complex(interpreter):
    assert interpreter.eval(AST("i*i")) == Term(Number(-1))
    assert interpreter.eval(AST("(2+3i)(1+4i)")) == Term(Number(-10, 11))
    assert interpreter.eval(AST("3(4-5i)")) == Term(Number(12, -15))
    assert interpreter.eval(AST("(-2+3i)(-1-4i)")) == Term(Number(14, 5))
    assert interpreter.eval(AST("(0+3i)(-1)")) == Term(Number(imag=-3))


def test_complex_scalar_division(interpreter):
    assert interpreter.eval(AST("(4+6i)/2")) == Term(Number(2, 3))
    assert interpreter.eval(AST("(8-4i)/-2")) == Term(Number(-4, 2))
    assert interpreter.eval(AST("(0+0i)/2")) == Term(Number())
    assert interpreter.eval(AST("(-6+9i)/3")) == Term(Number(-2, 3))


def test_complex_division(interpreter):
    assert interpreter.eval(AST("(4+2i)/(1-i)")) == Term(Number(1, 3))
    assert interpreter.eval(AST("(6+3i)/(-2+i)")) == Term(Number("-9/5", "-12/5"))
    assert interpreter.eval(AST("(-2+i)/(2+3i)")) == Term(Number("-1/13", "8/13"))
    assert interpreter.eval(AST("(3+4i)/(1-2i)")) == Term(Number(-1, 2))
    assert interpreter.eval(AST("0/(1+i)")) == Term(Number())
