from processing import AST
from utils import print_frac
from data_types import Number, Fraction, Term, Variable


def test_print_frac():
    assert print_frac(Fraction(1, 2)) == "0.5"
    assert print_frac(Fraction(3, 8)) == "0.375"
    assert print_frac(Fraction(1, 3)) == "(1/3)"
    assert print_frac(Fraction(2, 1)) == "2"
    assert print_frac(Fraction(3, 17)) == "(3/17)"


def test_print_number():
    assert str(Number(1, 2)) == "1+2i"
    assert str(Number(-1, 1)) == "-1+i"
    assert str(Number(0, 2)) == "2i"
    assert str(Number(1, 0)) == "1"
    assert str(Number(0, 0)) == "0"
    assert str(Number(0, 1)) == "i"
    assert str(Number(0, -1)) == "-i"
    assert str(Number("2/3", "0.5")) == "(2/3)+0.5i"
    assert str(Number(imag="1/3")) == "(1/3)i"


def test_print_variable():
    assert str(Term(Number(1), Variable("x"))) == "x"
    assert str(Term(Number(-1), Variable("y"))) == "-y"
    assert str(Term(Number(1), Variable("x"), Number(2))) == "x^2"
    assert str(Term(Number("0.5"), Variable("x"), Number(3))) == "0.5x^3"
    assert str(Term(Number("3/7"), Variable("x"), Number(1))) == "(3/7)x"
    assert str(Term(Number(2, 3), Variable("x"))) == "(2+3i)x"
    assert str(Term(Number(imag=1), Variable("x"))) == "(i)x"


def test_print_negative_exp():
    assert str(Term(Number(1), Variable("x"), Number(-1))) == "1/x"
    assert str(Term(Number(1), Variable("x"), Number(-2))) == "1/x^2"
    assert str(Term(Number("1.5"), Variable("x"), Number(-2))) == "3/2x^2"
    assert str(Term(Number("6/7"), Variable("x"), Number(-3))) == "6/7x^3"


def test_print_radical():
    assert str(Term(Number(1), Variable("x"), Number("0.5"))) == "2√x"
    assert str(Term(Number(1), Variable("x"), Number("-1/3"))) == "1/3√x"
    assert str(Term(Number("3.5"), Variable("x"), Number("1/3"))) == "3.5(3√x)"
    assert str(Term(Number("0.2"), Variable("x"), Number("2/3"))) == "0.2(3√x^2)"


def test_print_polynomial(interpreter):
    assert str(interpreter.eval(AST("x+1"))) == "(x + 1)"
    assert str(interpreter.eval(AST("47-600x"))) == "(-600x + 47)"
    assert (
        str(interpreter.eval(AST("1600+3x^3+y-12y^2"))) == "(3x^3 - 12y^2 + y + 1600)"
    )
    assert str(interpreter.eval(AST("x^2+3x+1"))) == "(x^2 + 3x + 1)"
    assert str(interpreter.eval(AST("3x+(3/(c+b))-1"))) == "(3x - 1 + 3/(c + b))"
