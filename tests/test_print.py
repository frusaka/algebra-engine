import pytest
from datatypes.nodes import Const, Const, Var
from processing import parser
from utils import print_frac


def test_print_frac():
    assert print_frac(Const(1, 2)) == "0.5"
    assert print_frac(Const(1, 3)) == "1/3"
    assert print_frac(Const(2, 1)) == "2"
    assert print_frac(Const(3, 8)) == "3/8"
    assert print_frac(Const(3, 17)) == "3/17"
    assert print_frac(Const(15, 26)) == "15/26"
    assert print_frac(Const(5, 14)) == "5/14"
    assert print_frac(Const(14, 48)) == "7/24"


def test_print_number():
    assert str(Const(1 + 2j)) == "(1+2i)"
    assert str(Const(-1 + 1j)) == "(-1+i)"
    # assert str(Const(1j, 10)) == "0.1i"
    assert str(Const(2j)) == "2i"
    assert str(Const(1)) == "1"
    assert str(Const(1j)) == "i"
    assert str(Const(0 - 11j)) == "-11i"
    assert str(Const(-0 - 1j)) == "-i"
    assert str(Const(4 + 3j, 6)) == "(4+3i)/6"
    assert str(Const(1j, 3)) == "i/3"


def test_print_variable():
    assert str(Var("x")) == "x"
    assert str(-Var("y")) == "-y"
    assert str(Var("x") ** 2) == "x²"
    assert str(Var("a") ** 3 / 2) == "a³/2"
    assert str(Const(3, 7) * Var("h") ** Const(1)) == "3h/7"
    assert str(Const(2 + 3j) * Var("x")) == "(2+3i)x"
    assert str(Const(1j) * Var("b")) == "ib"


def test_print_negative_exp():
    # assert str(1 * Var("x") ** -1) == "1/x"
    # assert str(Var("f") ** -2) == "1/f²"
    assert str(Const(3, 2) * Var("x") ** -2) == "3/(2x²)"
    assert str(Const(6, 7) * Var("k") ** Const(-3)) == "6/(7k³)"


def test_print_radical():
    assert str(Var("y") ** Const(1, 2)) == "√y"
    assert str(Const(2, 3) * Var("x") ** Const(-1, 3)) == "2/(3(³√x))"
    assert str((Const(7, 2) * Var("q") ** Const(1, 3))) == "7(³√q)/2"
    assert str(Const(1, 5) * Var("r") ** Const(2, 3)) == "(³√r²)/5"
    assert str(parser.eval("(x + c)^0.5")) == "√(c + x)"
    assert str(parser.eval("-1(x + c)^0.5")) == "-√(c + x)"
    assert str(parser.eval("2(x + c)^0.5")) == "2√(c + x)"
    assert str(parser.eval("-2(x + c)^0.5")) == "-2√(c + x)"
    assert str(parser.eval("5^(1/3) / 2")) == "(³√5)/2"
    assert str(parser.eval("2 * 5^0.5 / 3")) == "2√5/3"


def test_print_polynomial():
    assert str(parser.eval("x+1")) == "(x + 1)"
    assert str(parser.eval("47-600x")) == "(-600x + 47)"
    assert str(parser.eval("1600+3x^3+y-12y^2")) == "(3x³ - 12y² + y + 1600)"
    assert str(parser.eval("x^2+3x+1")) == "(x² + 3x + 1)"
    # assert str(parser.eval("3x+(3/(c+b))-1")) == "(3x - 1 + 3/(c + b))"


def test_print_product():
    assert str(parser.eval("-2xb")) == "-2bx"
    assert str(parser.eval("x^3*y^-5")) == "x³/y⁵"
    assert str(parser.eval("-10(m^-1*n^-1)")) == "-10/(mn)"
    assert str(parser.eval("(-2/3)(y^2n^-1)")) == "-2y²/(3n)"
    assert str(parser.eval("n/a - 5/4a")) == "(4n - 5)/(4a)"
    assert str(parser.eval("s^3*d^-5*z^2/3")) == "z²s³/(3d⁵)"
