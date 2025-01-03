from data_types.product import Product
from processing import AST
from data_types import Number, Variable, Polynomial, Term


def test_divide_polynomials(interpreter):
    # Dividing univariate polynomials
    assert interpreter.eval(AST("(5.2x^3 + 7x^2 - 31.2x - 42) / (3.5+2.6x)")) == Term(
        value=Polynomial(
            [
                Term(Number(2), Variable("x"), Number(2)),
                Term(Number(-12)),
            ]
        )
    )
    # Division with Remainder
    assert interpreter.eval(AST("(-6x^2 + 2x + 20)/(2-2x)")) == Term(
        value=Polynomial(
            [
                Term(Number(3), Variable("x")),
                Term(Number(2)),
                Term(
                    Number(16),
                    Polynomial([Term(Number(2)), Term(Number(-2), Variable("x"))]),
                    Number(-1),
                ),
            ]
        )
    )
    assert interpreter.eval(AST("(4x^2 - 17.64) / (2x - 4)")) == Term(
        value=Polynomial(
            [
                Term(Number(2), Variable("x")),
                Term(Number(4)),
                Term(
                    Number(-41, 25),
                    Polynomial([Term(Number(2), Variable("x")), Term(Number(-4))]),
                    Number(-1),
                ),
            ]
        )
    )
    # Divinding Product Polynomials
    assert interpreter.eval(AST("(-3.75c^2 + 18ab + 4.5abc - 15c)/(3+0.75c)")) == Term(
        value=Polynomial(
            [
                Term(
                    Number(6),
                    Product([Term(value=Variable("a")), Term(value=Variable("b"))]),
                ),
                Term(Number(-5), Variable("c")),
            ]
        )
    )


def test_multiply_polynomials(interpreter):
    # Multiplying univariate polynomials
    assert interpreter.eval(AST("(x + 1)(x + 2)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(3), Variable("x")),
                Term(Number(2)),
            ]
        )
    )
    assert interpreter.eval(AST("(2x+3)(0.5x - 5)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(-17, 2), Variable("x")),
                Term(Number(-15)),
            ]
        )
    )
    assert interpreter.eval(AST("(x + 1)(x + 2)(x + 3)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(3)),
                Term(Number(6), Variable("x"), Number(2)),
                Term(Number(11), Variable("x")),
                Term(6),
            ]
        )
    )
    # Multiplying multivariate polynomials
    assert interpreter.eval(AST("(x + 1)(y + 2)")) == Term(
        value=Polynomial(
            [
                Term(
                    value=Product(
                        [Term(value=Variable("x")), Term(value=Variable("y"))]
                    ),
                ),
                Term(Number(2), Variable("x")),
                Term(value=Variable("y")),
                Term(Number(2)),
            ]
        )
    )
    # Multiplication containing a fraction
    assert interpreter.eval(AST("(x - 4 + 12/(x + 4))(x+4)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(-4)),
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
                Term(1),
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
                Term(1),
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
