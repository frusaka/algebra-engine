import pytest
from processing import Interpreter, AST
from data_types import Number, Variable, Polynomial, Term


@pytest.fixture
def interpreter():
    return Interpreter()


def test_divide_univariate_polynomials(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) / (x + 1)")) == Polynomial(
        [Term(value=Variable("x")), Term()]
    )
    assert interpreter.eval(AST("(x^3 + 3x^2 + 3x + 1) / (x + 1)")) == Polynomial(
        [
            Term(Number(1), Variable("x"), Number(2)),
            Term(Number(2), Variable("x")),
            Term(),
        ]
    )
    assert interpreter.eval(AST("(x^2 - 1) / (x - 1)")) == Polynomial(
        [Term(value=Variable("x")), Term()]
    )


def test_multiply_polynomials(interpreter):
    assert interpreter.eval(AST("(x + 1) * (x + 2)")) == Polynomial(
        [
            Term(Number(1), Variable("x"), Number(2)),
            Term(Number(3), Variable("x")),
            Term(Number(2)),
        ]
    )
    assert interpreter.eval(AST("(y + 3) * (y + 4)")) == Polynomial(
        [
            Term(Number(1), Variable("y"), Number(2)),
            Term(Number(7), Variable("y")),
            Term(Number(12)),
        ]
    )
    assert interpreter.eval(AST("(z + 5) * (z + 6)")) == Polynomial(
        [
            Term(Number(1), Variable("z"), Number(2)),
            Term(Number(11), Variable("z")),
            Term(Number(30)),
        ]
    )


def test_subtract_polynomials(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) - (x + 1)")) == Polynomial(
        [
            Term(Number(1), Variable("x"), Number(2)),
            Term(Number(1), Variable("x")),
        ]
    )
    assert interpreter.eval(AST("(y^2 + 3y + 2) - (y + 2)")) == Polynomial(
        [
            Term(Number(1), Variable("y"), Number(2)),
            Term(Number(2), Variable("y")),
        ]
    )
    assert interpreter.eval(AST("(z^2 + 4z + 3) - (z + 3)")) == Polynomial(
        [
            Term(Number(1), Variable("z"), Number(2)),
            Term(Number(3), Variable("z")),
        ]
    )


def test_exponentiation(interpreter):
    assert interpreter.eval(AST("(x + 1)^2")) == Polynomial(
        [
            Term(Number(1), Variable("x"), Number(2)),
            Term(Number(2), Variable("x")),
            Term(),
        ]
    )
    assert interpreter.eval(AST("(y + 2)^2")) == Polynomial(
        [
            Term(Number(1), Variable("y"), Number(2)),
            Term(Number(4), Variable("y")),
            Term(Number(4)),
        ]
    )
    assert interpreter.eval(AST("(z + 3)^2")) == Polynomial(
        [
            Term(Number(1), Variable("z"), Number(2)),
            Term(Number(6), Variable("z")),
            Term(Number(9)),
        ]
    )


def test_complex_expression(interpreter):
    assert interpreter.eval(AST("2x^2 + 3x - 5 + x^2 - x + 4")) == Polynomial(
        [
            Term(Number(3), Variable("x"), Number(2)),
            Term(Number(2), Variable("x")),
            Term(Number(-1)),
        ]
    )
    assert interpreter.eval(AST("3y^2 + 4y - 6 + y^2 - y + 5")) == Polynomial(
        [
            Term(Number(4), Variable("y"), Number(2)),
            Term(Number(3), Variable("y")),
            Term(Number(-1)),
        ]
    )
    assert interpreter.eval(AST("4z^2 + 5z - 7 + z^2 - z + 6")) == Polynomial(
        [
            Term(Number(5), Variable("z"), Number(2)),
            Term(Number(4), Variable("z")),
            Term(Number(-1)),
        ]
    )


def test_nested_expressions(interpreter):
    assert interpreter.eval(AST("((x + 1) * (x - 1))^2")) == Polynomial(
        [
            Term(Number(1), Variable("x"), Number(4)),
            Term(Number(-2), Variable("x"), Number(2)),
            Term(),
        ]
    )
    assert interpreter.eval(AST("((y + 2) * (y - 2))^2")) == Polynomial(
        [
            Term(Number(1), Variable("y"), Number(4)),
            Term(Number(-8), Variable("y"), Number(2)),
            Term(Number(16)),
        ]
    )
    assert interpreter.eval(AST("((z + 3) * (z - 3))^2")) == Polynomial(
        [
            Term(Number(1), Variable("z"), Number(4)),
            Term(Number(-18), Variable("z"), Number(2)),
            Term(Number(81)),
        ]
    )


def test_divide_univariate_polynomials(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) / (x + 1)")) == Term(
        value=Polynomial([Term(Number(1), Variable("x"), Number(1)), Term()])
    )
    assert interpreter.eval(AST("(x^2 - 1) / (x - 1)")) == Term(
        value=Polynomial([Term(Number(1), Variable("x"), Number(1)), Term()])
    )
    assert interpreter.eval(AST("(x^3 + 3x^2 + 3x + 1) / (x + 1)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(),
            ]
        )
    )


def test_multiply_polynomials(interpreter):
    assert interpreter.eval(AST("(x + 1) * (x + 2)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(3), Variable("x")),
                Term(value=Number(2)),
            ]
        )
    )
    assert interpreter.eval(AST("(y + 3) * (y + 4)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("y"), Number(2)),
                Term(Number(7), Variable("y")),
                Term(value=Number(12)),
            ]
        )
    )

    assert interpreter.eval(AST("(z + 5) * (z + 6)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(2)),
                Term(Number(11), Variable("z")),
                Term(value=Number(30)),
            ]
        )
    )


def test_subtract_polynomials(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) - (x + 1)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("x")),
            ]
        )
    )
    assert interpreter.eval(AST("(y^2 + 3y + 2) - (y + 2)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("y"), Number(2)),
                Term(Number(2), Variable("y")),
            ]
        )
    )
    assert interpreter.eval(AST("(z^2 + 4z + 3) - (z + 3)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(2)),
                Term(Number(3), Variable("z")),
            ]
        )
    )


def test_exponentiation(interpreter):
    assert interpreter.eval(AST("(x + 1)^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(),
            ]
        )
    )
    assert interpreter.eval(AST("(y + 2)^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("y"), Number(2)),
                Term(Number(4), Variable("y")),
                Term(Number(4)),
            ]
        )
    )
    assert interpreter.eval(AST("(z + 3)^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(2)),
                Term(Number(6), Variable("z")),
                Term(Number(9)),
            ]
        )
    )


def test_complex_expression(interpreter):
    assert interpreter.eval(AST("2x^2 + 3x - 5 + x^2 - x + 4")) == Term(
        value=Polynomial(
            [
                Term(Number(3), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(Number(-1)),
            ]
        )
    )
    assert interpreter.eval(AST("3y^2 + 4y - 6 + y^2 - y + 5")) == Term(
        value=Polynomial(
            [
                Term(Number(4), Variable("y"), Number(2)),
                Term(Number(3), Variable("y")),
                Term(Number(-1)),
            ]
        )
    )
    assert interpreter.eval(AST("4z^2 + 5z - 7 + z^2 - z + 6")) == Term(
        value=Polynomial(
            [
                Term(Number(5), Variable("z"), Number(2)),
                Term(Number(4), Variable("z")),
                Term(Number(-1)),
            ]
        )
    )


def test_nested_expressions(interpreter):
    assert interpreter.eval(AST("((x + 1) * (x - 1))^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(4)),
                Term(Number(-2), Variable("x"), Number(2)),
                Term(),
            ]
        )
    )
    assert interpreter.eval(AST("((y + 2) * (y - 2))^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("y"), Number(4)),
                Term(Number(-8), Variable("y"), Number(2)),
                Term(Number(16)),
            ]
        )
    )

    assert interpreter.eval(AST("((z + 3) * (z - 3))^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(4)),
                Term(Number(-18), Variable("z"), Number(2)),
                Term(Number(81)),
            ]
        )
    )


def test_polynomial_variable_exponents(interpreter):
    assert interpreter.eval(AST("x^a * x^b")) == Term(
        Number(1),
        Variable("x"),
        Term(value=Polynomial([Term(value=Variable("a")), Term(value=Variable("b"))])),
    )
    assert interpreter.eval(AST("y^m * y^n")) == Term(
        Number(1),
        Variable("y"),
        Term(value=Polynomial([Term(value=Variable("m")), Term(value=Variable("n"))])),
    )
    assert interpreter.eval(AST("z^p / z^q")) == Term(
        Number(1),
        Variable("z"),
        Term(
            value=Polynomial(
                [Term(value=Variable("p")), Term(coef=Number(-1), value=Variable("q"))]
            )
        ),
    )


def test_polynomial_multiple_terms(interpreter):
    assert interpreter.eval(AST("x^2 + x^3")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("x"), Number(3)),
            ]
        )
    )
    assert interpreter.eval(AST("z^5 + z^3 + z + 1")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(5)),
                Term(Number(1), Variable("z"), Number(3)),
                Term(Number(1), Variable("z")),
                Term(Number(1)),
            ]
        )
    )
    assert interpreter.eval(AST("x^2 + y^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("y"), Number(2)),
            ]
        )
    )
    assert interpreter.eval(AST("x^3 + z^3")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(3)),
                Term(Number(1), Variable("z"), Number(3)),
            ]
        )
    )


def test_multiply_polynomials_different_variables(interpreter):
    assert interpreter.eval(AST("x^2 * y^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("y"), Number(2)),
            ]
        )
    )
    assert interpreter.eval(AST("x^3 * z^3")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(3)),
                Term(Number(1), Variable("z"), Number(3)),
            ]
        )
    )


def test_divide_polynomials_different_variables(interpreter):
    assert interpreter.eval(AST("x^2 / y^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("y"), Number(-2)),
            ]
        )
    )
    assert interpreter.eval(AST("x^3 / z^3")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(3)),
                Term(Number(1), Variable("z"), Number(-3)),
            ]
        )
    )


def test_power_polynomials_different_variables(interpreter):
    assert interpreter.eval(AST("(x^2)^y")) == Term(
        value=Variable("x"), exp=Term(Number(2), Variable("y"))
    )
    assert interpreter.eval(AST("(y^3)^z")) == Term(
        value=Variable("y"), exp=Term(Number(3), Variable("z"))
    )
