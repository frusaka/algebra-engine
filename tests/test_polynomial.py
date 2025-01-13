import pytest
from processing import AST
from data_types import Number, Variable, Polynomial, Product, AlgebraObject


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
                    Number(8),
                    Polynomial(
                        [
                            AlgebraObject(Number(-1), Variable("x")),
                            AlgebraObject(Number(1)),
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
                    Number(-41),
                    Polynomial(
                        [
                            AlgebraObject(Number(50), Variable("x")),
                            AlgebraObject(Number(-100)),
                        ]
                    ),
                    Number(-1),
                ),
            ]
        )
    )
    # Numerator with lower degrees
    assert interpreter.eval(AST("(x - 1)/(x - 1)^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("x")),
                AlgebraObject(Number(-1)),
            ]
        ),
        exp=Number(-1),
    )
    assert interpreter.eval(
        AST("(3(x - 4) - 7(x - 4))/(x^2 - 8x + 16)")
    ) == AlgebraObject(
        Number(4),
        Polynomial(
            [
                AlgebraObject(Number(-1), value=Variable("x")),
                AlgebraObject(Number(4)),
            ]
        ),
        Number(-1),
    )
    assert interpreter.eval(AST("(3(x + 6) -0.5(x + 6))/(x + 6)^2")) == AlgebraObject(
        Number(5),
        Polynomial(
            [
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(Number(12)),
            ]
        ),
        Number(-1),
    )


def test_divide_multivariate(interpreter):
    assert interpreter.eval(AST("(3n + 3c)/(n+c)")) == AlgebraObject(Number(3))
    assert interpreter.eval(AST("(n+c)/(3n+3c)")) == AlgebraObject(Number("1/3"))
    assert interpreter.eval(AST("(a^3 + b^3)/(a + b)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("b"), exp=Number(2)),
                AlgebraObject(value=Variable("a"), exp=Number(2)),
                AlgebraObject(
                    Number(-1),
                    Product(
                        [
                            AlgebraObject(value=Variable("a")),
                            AlgebraObject(value=Variable("b")),
                        ]
                    ),
                ),
            ]
        )
    )

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
    # Nested
    assert interpreter.eval(AST("((z + 3)(z - 3))^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("z"), Number(4)),
                AlgebraObject(Number(-18), Variable("z"), Number(2)),
                AlgebraObject(Number(81)),
            ]
        )
    )
    # Negative Exponents
    assert interpreter.eval(AST("(x+1)^-1(x^2+2x+1)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("x")),
                AlgebraObject(Number(1)),
            ]
        )
    )
    expected = AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(
                    Number(3),
                    Product(
                        [AlgebraObject(Variable("x")), AlgebraObject(Variable("y"))]
                    ),
                ),
                AlgebraObject(Number(-4), Variable("y")),
            ]
        )
    )
    assert interpreter.eval(AST("(x+2)^-1(3x-4)(xy+2y)")) == expected
    assert interpreter.eval(AST("(3x-4)(x+2)^-1(xy+2y)")) == expected
    assert interpreter.eval(AST("(xy+2y)(3x-4)(x+2)^-1")) == expected


def test_merge_polynomial(interpreter):
    assert interpreter.eval(AST("(x^2 + 2x + 1) - (x + 1)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(1), Variable("x")),
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
    assert interpreter.eval(AST("2(2√(x + c)) - 1.5(2√(x + c))")) == AlgebraObject(
        Number("0.5"),
        Polynomial(
            [
                AlgebraObject(value=Variable("x")),
                AlgebraObject(value=Variable("c")),
            ]
        ),
        Number("0.5"),
    )
