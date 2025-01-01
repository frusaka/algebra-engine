import pytest
from processing import Interpreter, AST
from data_types import Number, Variable, Term


@pytest.fixture
def interpreter():
    return Interpreter()


def test_simplify_fractions(interpreter):
    assert interpreter.eval(AST("4/8")) == Term(Number(1, 2))
    assert interpreter.eval(AST("10/5")) == Term(Number(2))
    assert interpreter.eval(AST("15/3")) == Term(Number(5))


def test_merge_like_terms(interpreter):
    assert interpreter.eval(AST("2x + 3x")) == Term(Number(5), Variable("x"))
    assert interpreter.eval(AST("4y + 2y")) == Term(Number(6), Variable("y"))
    assert interpreter.eval(AST("5z - 3z")) == Term(Number(2), Variable("z"))


def test_divide_variables(interpreter):
    assert interpreter.eval(AST("x^2 / x")) == Term(Number(1), Variable("x"), Number(1))
    assert interpreter.eval(AST("y^3 / y")) == Term(Number(1), Variable("y"), Number(2))
    assert interpreter.eval(AST("z^4 / z^2")) == Term(
        Number(1), Variable("z"), Number(2)
    )


def test_handle_exponents(interpreter):
    assert interpreter.eval(AST("x^2 * x^3")) == Term(
        Number(1), Variable("x"), Number(5)
    )
    assert interpreter.eval(AST("y^4 * y^2")) == Term(
        Number(1), Variable("y"), Number(6)
    )
    assert interpreter.eval(AST("z^5 * z^3")) == Term(
        Number(1), Variable("z"), Number(8)
    )


def test_simplify_constants(interpreter):
    assert interpreter.eval(AST("10 + 5 - 3")) == Term(Number(12))
    assert interpreter.eval(AST("20 - 4 + 2")) == Term(Number(18))
    assert interpreter.eval(AST("30 + 10 - 5")) == Term(Number(35))


def test_multiply_variables(interpreter):
    assert interpreter.eval(AST("x * x")) == Term(Number(1), Variable("x"), Number(2))
    assert interpreter.eval(AST("y * y")) == Term(Number(1), Variable("y"), Number(2))
    assert interpreter.eval(AST("z * z")) == Term(Number(1), Variable("z"), Number(2))


def test_zero_exponent(interpreter):
    assert interpreter.eval(AST("x^0")) == Term()
    assert interpreter.eval(AST("y^0")) == Term()
    assert interpreter.eval(AST("12^0")) == Term()
    assert interpreter.eval(AST("0^0")) == Term()


def test_zero_coefficient(interpreter):
    assert interpreter.eval(AST("0 * x^2")) == Term(Number(0))
    assert interpreter.eval(AST("0 * y^3")) == Term(Number(0))
    assert interpreter.eval(AST("0 * z^4")) == Term(Number(0))


def test_negative_exponent(interpreter):
    assert interpreter.eval(AST("x^-2")) == Term(Number(1), Variable("x"), Number(-2))
    assert interpreter.eval(AST("y^-3")) == Term(Number(1), Variable("y"), Number(-3))
    assert interpreter.eval(AST("z^-4")) == Term(Number(1), Variable("z"), Number(-4))


def test_fractional_exponent(interpreter):
    assert interpreter.eval(AST("x^(1/2)")) == Term(
        Number(1), Variable("x"), Number(1, 2)
    )
    assert interpreter.eval(AST("y^(1/3)")) == Term(
        Number(1), Variable("y"), Number(1, 3)
    )
    assert interpreter.eval(AST("z^(6/8)")) == Term(
        Number(1), Variable("z"), Number(3, 4)
    )


def test_handle_exponents(interpreter):
    assert interpreter.eval(AST("x^2 * x^3")) == Term(
        Number(1),
        Variable("x"),
        Number(5),
    )
    assert interpreter.eval(AST("y^4 * y^2")) == Term(
        Number(1),
        Variable("y"),
        Number(6),
    )
    assert interpreter.eval(AST("z^5 * z^3")) == Term(
        Number(1),
        Variable("z"),
        Number(8),
    )


def test_simplify_constants(interpreter):
    assert interpreter.eval(AST("10 + 5 - 3")) == Term(Number(12))
    assert interpreter.eval(AST("20 - 4 + 2")) == Term(Number(18))
    assert interpreter.eval(AST("30 + 10 - 5")) == Term(Number(35))


def test_multiply_variables(interpreter):
    assert interpreter.eval(AST("x * x")) == Term(Number(1), Variable("x"), Number(2))
    assert interpreter.eval(AST("y * y")) == Term(Number(1), Variable("y"), Number(2))
    assert interpreter.eval(AST("z * z")) == Term(Number(1), Variable("z"), Number(2))


def test_zero_exponent(interpreter):
    expected = Term(value=Number(1))
    assert interpreter.eval(AST("x^0")) == expected
    assert interpreter.eval(AST("y^0")) == expected
    assert interpreter.eval(AST("12^0")) == expected
    assert interpreter.eval(AST("0^0")) == expected


def test_zero_coefficient(interpreter):
    expected = Term(value=Number(0))
    assert interpreter.eval(AST("0 * x^2")) == expected
    assert interpreter.eval(AST("0 * y^3")) == expected
    assert interpreter.eval(AST("0 * z^4")) == expected


def test_negative_exponent(interpreter):
    assert interpreter.eval(AST("x^-2")) == Term(Number(1), Variable("x"), Number(-2))
    assert interpreter.eval(AST("y^-3")) == Term(Number(1), Variable("y"), Number(-3))
    assert interpreter.eval(AST("z^-4")) == Term(Number(1), Variable("z"), Number(-4))


def test_fractional_exponent(interpreter):
    assert interpreter.eval(AST("x^(1/2)")) == Term(
        Number(1), Variable("x"), Number(1, 2)
    )
    assert interpreter.eval(AST("y^(1/3)")) == Term(
        Number(1), Variable("y"), Number(1, 3)
    )
    assert interpreter.eval(AST("z^(1/4)")) == Term(
        Number(1), Variable("z"), Number(1, 4)
    )
