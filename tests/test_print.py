import pytest
from processing import AST
from utils import print_frac
from data_types import Number, Fraction, Term, Variable


def test_print_frac():
    assert print_frac(Fraction(1, 2)) == "0.5"
    assert print_frac(Fraction(3, 8)) == "0.375"
    assert print_frac(Fraction(1, 3)) == "1/3"
    assert print_frac(Fraction(2, 1)) == "2"
    assert print_frac(Fraction(3, 17)) == "3/17"
    assert print_frac(Fraction(15, 26)) == "15/26"
    assert print_frac(Fraction(5, 14)) == "5/14"
    assert print_frac(Fraction(14, 48)) == "7/24"


def test_print_number():
    assert str(Number(complex(1, 2))) == "(1+2i)"
    assert str(Number(complex(-1, 1))) == "(-1+i)"
    assert str(Number(complex(0, 2))) == "2i"
    assert str(Number(1)) == "1"
    assert str(Number(complex(0, 1))) == "i"
    assert str(Number(complex(0, -11))) == "-11i"
    assert str(Number(complex(0, -1))) == "-i"
    assert str(Number(complex(4, 3), 6)) == "(4+3i)/6"
    assert str(Number(complex(0, 1), 3)) == "i/3"


def test_print_variable():
    assert str(Term(Number(1), Variable("x"))) == "x"
    assert str(Term(Number(-1), Variable("y"))) == "-y"
    assert str(Term(Number(1), Variable("x"), Number(2))) == "x^2"
    assert str(Term(Number("0.5"), Variable("a"), Number(3))) == "0.5a^3"
    assert str(Term(Number("3/7"), Variable("h"), Number(1))) == "3h/7"
    assert str(Term(Number(complex(2, 3)), Variable("x"))) == "(2+3i)x"
    assert str(Term(Number(complex(0, 1)), Variable("b"))) == "(i)b"


def test_print_negative_exp():
    assert str(Term(Number(1), Variable("x"), Number(-1))) == "1/x"
    assert str(Term(Number(1), Variable("f"), Number(-2))) == "1/f^2"
    assert str(Term(Number("1.5"), Variable("x"), Number(-2))) == "3/2x^2"
    assert str(Term(Number("6/7"), Variable("k"), Number(-3))) == "6/7k^3"


def test_print_radical(processor):
    assert str(Term(Number(1), Variable("y"), Number("0.5"))) == "2√y"
    assert str(Term(Number(1), Variable("x"), Number("-1/3"))) == "1/3√x"
    assert str(Term(Number("3.5"), Variable("q"), Number("1/3"))) == "3.5(3√q)"
    assert str(Term(Number("0.2"), Variable("r"), Number("2/3"))) == "0.2(3√r^2)"
    assert str(processor.eval(AST("2√(x + c)"))) == "2√(x + c)"
    assert str(processor.eval(AST("-1(2√(x + c))"))) == "-2√(x + c)"
    assert str(processor.eval(AST("2(2√(x + c))"))) == "2(2√(x + c))"
    assert str(processor.eval(AST("-2(2√(x + c))"))) == "-2(2√(x + c))"
    assert str(processor.eval(AST("2√5 / 2"))) == "0.5(2√5)"
    assert str(processor.eval(AST("2 * 2√5 / 3"))) == "2(2√5)/3"


def test_print_polynomial(processor):
    assert str(processor.eval(AST("x+1"))) == "(x + 1)"
    assert str(processor.eval(AST("47-600x"))) == "(-600x + 47)"
    assert str(processor.eval(AST("1600+3x^3+y-12y^2"))) == "(3x^3 - 12y^2 + y + 1600)"
    assert str(processor.eval(AST("x^2+3x+1"))) == "(x^2 + 3x + 1)"
    assert str(processor.eval(AST("3x+(3/(c+b))-1"))) == "(3x - 1 + 3/(c + b))"


@pytest.mark.xfail(reason="Fine alternative")
def test_print_product(processor):
    assert str(processor.eval(AST("-2xb"))) == "-2bx"
    assert str(processor.eval(AST("x^3*y^-5"))) == "x^3/y^5"
    assert str(processor.eval(AST("-10(m^-1*n^-1)"))) == "-10/mn"
    assert str(processor.eval(AST("(-2/3)(y^2n^-1)"))) == "-2y^2/3n"
    assert str(processor.eval(AST("n/a - 5/4a"))) == "(4n - 5)/4a"
    assert str(processor.eval(AST("s^3*d^-5*z^2/3"))) == "(z^2s^3)/3d^5"
