import pytest
from processing import AST
from data_types import Number, Variable, Polynomial, Product, Term


def test_divide_polynomials(processor):
    # Dividing univariate polynomials
    assert processor.eval(AST("(5.2x^3 + 7x^2 - 31.2x - 42) / (3.5+2.6x)")) == Term(
        value=Polynomial(
            [
                Term(Number(2), Variable("x"), Number(2)),
                Term(Number(-12)),
            ]
        )
    )
    # Division with Remainder
    assert processor.eval(AST("(-6x^2 + 2x + 20)/(2-2x)")) == Term(
        value=Polynomial(
            [
                Term(Number(3), Variable("x")),
                Term(Number(2)),
                Term(
                    Number(-8),
                    Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(-1)),
                        ]
                    ),
                    Number(-1),
                ),
            ]
        )
    )
    assert processor.eval(AST("(4x^2 - 17.64) / (2x - 4)")) == Term(
        value=Polynomial(
            [
                Term(Number(2), Variable("x")),
                Term(Number(4)),
                Term(
                    Number(-41),
                    Polynomial(
                        [
                            Term(Number(50), Variable("x")),
                            Term(Number(-100)),
                        ]
                    ),
                    Number(-1),
                ),
            ]
        )
    )
    # Numerator with lower degrees
    assert processor.eval(AST("(x - 1)/(x - 1)^2")) == Term(
        value=Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(-1)),
            ]
        ),
        exp=Number(-1),
    )
    assert processor.eval(AST("(3(x - 4) - 7(x - 4))/(x^2 - 8x + 16)")) == Term(
        Number(-4),
        Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(-4)),
            ]
        ),
        Number(-1),
    )
    assert processor.eval(AST("(3(x + 6) -0.5(x + 6))/(x + 6)^2")) == Term(
        Number(5),
        Polynomial(
            [
                Term(Number(2), Variable("x")),
                Term(Number(12)),
            ]
        ),
        Number(-1),
    )


def test_divide_multivariate(processor):
    assert processor.eval(AST("(3n + 3c)/(n+c)")) == Term(Number(3))
    assert processor.eval(AST("(n+c)/(3n+3c)")) == Term(Number("1/3"))
    assert processor.eval(AST("(a^3 + b^3)/(a + b)")) == Term(
        value=Polynomial(
            [
                Term(value=Variable("b"), exp=Number(2)),
                Term(value=Variable("a"), exp=Number(2)),
                Term(
                    Number(-1),
                    Product(
                        [
                            Term(value=Variable("a")),
                            Term(value=Variable("b")),
                        ]
                    ),
                ),
            ]
        )
    )

    assert processor.eval(AST("(-3.75c^2 + 18ab + 4.5abc - 15c)/(3+0.75c)")) == Term(
        value=Polynomial(
            [
                Term(
                    Number(6),
                    Product(
                        [
                            Term(value=Variable("a")),
                            Term(value=Variable("b")),
                        ]
                    ),
                ),
                Term(Number(-5), Variable("c")),
            ]
        )
    )


def test_multiply_polynomials(processor):
    # Multiplying univariate polynomials
    assert processor.eval(AST("(2x+3)(0.5x - 5)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number("-17/2"), Variable("x")),
                Term(Number(-15)),
            ]
        )
    )
    assert processor.eval(AST("(x + 1)(x + 2)(x + 3)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(3)),
                Term(Number(6), Variable("x"), Number(2)),
                Term(Number(11), Variable("x")),
                Term(Number(6)),
            ]
        )
    )
    # Multiplying multivariate polynomials
    assert processor.eval(AST("(x + 1)(y + 2)")) == Term(
        value=Polynomial(
            [
                Term(
                    value=Product(
                        [
                            Term(value=Variable("x")),
                            Term(value=Variable("y")),
                        ]
                    ),
                ),
                Term(Number(2), Variable("x")),
                Term(value=Variable("y")),
                Term(Number(2)),
            ]
        )
    )
    # Multiplication containing a fraction
    assert processor.eval(AST("(x - 4 + 12/(x + 4))(x+4)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(-4)),
            ]
        )
    )
    # Nested
    assert processor.eval(AST("((z + 3)(z - 3))^2")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(4)),
                Term(Number(-18), Variable("z"), Number(2)),
                Term(Number(81)),
            ]
        )
    )
    # Negative Exponents
    assert processor.eval(AST("(x+1)^-1(x^2+2x+1)")) == Term(
        value=Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(1)),
            ]
        )
    )
    expected = Term(
        value=Polynomial(
            [
                Term(
                    Number(3),
                    Product([Term(Variable("x")), Term(Variable("y"))]),
                ),
                Term(Number(-4), Variable("y")),
            ]
        )
    )
    assert processor.eval(AST("(x+2)^-1(3x-4)(xy+2y)")) == expected
    assert processor.eval(AST("(3x-4)(x+2)^-1(xy+2y)")) == expected
    assert processor.eval(AST("(xy+2y)(3x-4)(x+2)^-1")) == expected


def test_merge_polynomial(processor):
    assert processor.eval(AST("(x^2 + 2x + 1) - (x + 1)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("x")),
            ]
        )
    )
    assert processor.eval(AST("(z^2 + 4z + 3) - (z + 3)")) == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(2)),
                Term(Number(3), Variable("z")),
            ]
        )
    )
    assert processor.eval(AST("2x^2 + 3x - 5 + x^2 - x + 4")) == Term(
        value=Polynomial(
            [
                Term(Number(3), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(Number(-1)),
            ]
        )
    )
    assert processor.eval(AST("3y^2 + 4y - 6 + y^2 - y + 5")) == Term(
        value=Polynomial(
            [
                Term(Number(4), Variable("y"), Number(2)),
                Term(Number(3), Variable("y")),
                Term(Number(-1)),
            ]
        )
    )
    assert processor.eval(AST("2(2√(x + c)) - 1.5(2√(x + c))")) == Term(
        Number("0.5"),
        Polynomial(
            [
                Term(value=Variable("x")),
                Term(value=Variable("c")),
            ]
        ),
        Number("0.5"),
    )
