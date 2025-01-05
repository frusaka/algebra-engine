import pytest
from data_types.product import Product
from processing import AST
from data_types import Number, Variable, Polynomial, AlgebraObject


def test_divide_polynomials(interpreter):
    # Dividing univariate polynomials
    assert interpreter.eval(
        AST("(5.2x^3 + 7x^2 - 31.2x - 42) / (3.5+2.6x)")
    ) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(2), Variable("x"), Number(2)),
                AlgebraObject(Number(-12)),
            ]
        )
    )
    # Division with Remainder
    assert interpreter.eval(AST("(-6x^2 + 2x + 20)/(2-2x)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(3), Variable("x")),
                AlgebraObject(Number(2)),
                AlgebraObject(
                    Number(16),
                    Polynomial(
                        [
                            AlgebraObject(Number(2)),
                            AlgebraObject(Number(-2), Variable("x")),
                        ]
                    ),
                    Number(-1),
                ),
            ]
        )
    )
    assert interpreter.eval(AST("(4x^2 - 17.64) / (2x - 4)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(Number(4)),
                AlgebraObject(
                    Number("-41/25"),
                    Polynomial(
                        [
                            AlgebraObject(Number(2), Variable("x")),
                            AlgebraObject(Number(-4)),
                        ]
                    ),
                    Number(-1),
                ),
            ]
        )
    )


@pytest.mark.xfail(reason="Division of product polynomials is not yet fully supported")
def test_divide_product_polynomials(interpreter):
    # Divinding Product Polynomials
    assert interpreter.eval(
        AST("(-3.75c^2 + 18ab + 4.5abc - 15c)/(3+0.75c)")
    ) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(
                    Number(6),
                    Product(
                        [
                            AlgebraObject(value=Variable("a")),
                            AlgebraObject(value=Variable("b")),
                        ]
                    ),
                ),
                AlgebraObject(Number(-5), Variable("c")),
            ]
        )
    )


def test_multiply_polynomials(interpreter):
    # Multiplying univariate polynomials
    assert interpreter.eval(AST("(x + 1)(x + 2)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(3), Variable("x")),
                AlgebraObject(Number(2)),
            ]
        )
    )
    assert interpreter.eval(AST("(2x+3)(0.5x - 5)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number("-17/2"), Variable("x")),
                AlgebraObject(Number(-15)),
            ]
        )
    )
    assert interpreter.eval(AST("(x + 1)(x + 2)(x + 3)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(3)),
                AlgebraObject(Number(6), Variable("x"), Number(2)),
                AlgebraObject(Number(11), Variable("x")),
                AlgebraObject(Number(6)),
            ]
        )
    )
    # Multiplying multivariate polynomials
    assert interpreter.eval(AST("(x + 1)(y + 2)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(
                    value=Product(
                        [
                            AlgebraObject(value=Variable("x")),
                            AlgebraObject(value=Variable("y")),
                        ]
                    ),
                ),
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(value=Variable("y")),
                AlgebraObject(Number(2)),
            ]
        )
    )
    # Multiplication containing a fraction
    assert interpreter.eval(AST("(x - 4 + 12/(x + 4))(x+4)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(-4)),
            ]
        )
    )


def test_subtract_polynomials(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) - (x + 1)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(1), Variable("x")),
            ]
        )
    )
    assert interpreter.eval(AST("(y^2 + 3y + 2) - (y + 2)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("y"), Number(2)),
                AlgebraObject(Number(2), Variable("y")),
            ]
        )
    )
    assert interpreter.eval(AST("(z^2 + 4z + 3) - (z + 3)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("z"), Number(2)),
                AlgebraObject(Number(3), Variable("z")),
            ]
        )
    )


def test_exponentiation(interpreter):
    assert interpreter.eval(AST("(x + 1)^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(),
            ]
        )
    )
    assert interpreter.eval(AST("(y + 2)^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("y"), Number(2)),
                AlgebraObject(Number(4), Variable("y")),
                AlgebraObject(Number(4)),
            ]
        )
    )
    assert interpreter.eval(AST("(z + 3)^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("z"), Number(2)),
                AlgebraObject(Number(6), Variable("z")),
                AlgebraObject(Number(9)),
            ]
        )
    )


def test_complex_expression(interpreter):
    assert interpreter.eval(AST("2x^2 + 3x - 5 + x^2 - x + 4")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(3), Variable("x"), Number(2)),
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(Number(-1)),
            ]
        )
    )
    assert interpreter.eval(AST("3y^2 + 4y - 6 + y^2 - y + 5")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(4), Variable("y"), Number(2)),
                AlgebraObject(Number(3), Variable("y")),
                AlgebraObject(Number(-1)),
            ]
        )
    )
    assert interpreter.eval(AST("4z^2 + 5z - 7 + z^2 - z + 6")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(5), Variable("z"), Number(2)),
                AlgebraObject(Number(4), Variable("z")),
                AlgebraObject(Number(-1)),
            ]
        )
    )


def test_nested_expressions(interpreter):
    assert interpreter.eval(AST("((x + 1) * (x - 1))^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(4)),
                AlgebraObject(Number(-2), Variable("x"), Number(2)),
                AlgebraObject(),
            ]
        )
    )
    assert interpreter.eval(AST("((y + 2) * (y - 2))^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("y"), Number(4)),
                AlgebraObject(Number(-8), Variable("y"), Number(2)),
                AlgebraObject(Number(16)),
            ]
        )
    )

    assert interpreter.eval(AST("((z + 3) * (z - 3))^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("z"), Number(4)),
                AlgebraObject(Number(-18), Variable("z"), Number(2)),
                AlgebraObject(Number(81)),
            ]
        )
    )
