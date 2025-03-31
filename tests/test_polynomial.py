import pytest
from datatypes import Number, Variable, Polynomial, Product, Term
from processing import AST


def test_divide_polynomial():
    assert AST("(5.2x^3 + 7x^2 - 31.2x - 42) / (3.5+2.6x)").eval() == Term(
        value=Polynomial(
            [
                Term(Number(2), Variable("x"), Number(2)),
                Term(Number(-12)),
            ]
        )
    )
    # Numerator with lower degrees
    assert AST("(x - 1)/(x - 1)^2").eval() == Term(
        value=Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(-1)),
            ]
        ),
        exp=Number(-1),
    )
    assert AST("(3(x - 4) - 7(x - 4))/(x^2 - 8x + 16)").eval() == Term(
        Number(-4),
        Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(-4)),
            ]
        ),
        Number(-1),
    )
    assert AST("(3(x + 6) -0.5(x + 6))/(x + 6)^2").eval() == Term(
        Number(5),
        Polynomial(
            [
                Term(Number(2), Variable("x")),
                Term(Number(12)),
            ]
        ),
        Number(-1),
    )
    assert AST("(0.3x^2 + 2.4x + 4.5) / (0.2x^3 + 0.6x^2 - 5x - 15)").eval() == Term(
        Number(3),
        Polynomial(
            [
                Term(Number(2), Variable("x")),
                Term(Number(-10)),
            ]
        ),
        Number(-1),
    )
    assert AST("(x^2 + 0.4x - 7.8) / (x^3 - 8.2x^2 + 22.36x - 20.28)").eval() == Term(
        value=Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(Number(5), Variable("x")),
                            Term(Number(15)),
                        ]
                    )
                ),
                Term(
                    value=Polynomial(
                        [
                            Term(Number(5), Variable("x"), Number(2)),
                            Term(Number(-28), Variable("x")),
                            Term(Number(39)),
                        ]
                    ),
                    exp=Number(-1),
                ),
            ]
        )
    )
    # Division with Remainder : Engine no longer outputs mixed Polynomials
    # Coming back soon
    # assert AST("(-6x^2 + 2x + 20)/(2-2x)").eval()
    # assert AST("(4x^2 - 17.64) / (2x - 4)").eval()
    assert AST("((x-3)(x+5)+(x-3))/(x-3)(x+5)").eval() == Term(
        value=Product(
            [
                Term(
                    value=Polynomial([Term(value=Variable("x")), Term(Number(6))]),
                ),
                Term(
                    value=Polynomial([Term(value=Variable("x")), Term(Number(5))]),
                    exp=Number(-1),
                ),
            ]
        )
    )
    assert AST("(x^2 - 4)/(x^2 + 8x - 20)").eval() == Term(
        value=Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(2)),
                        ]
                    ),
                ),
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(10)),
                        ]
                    ),
                    exp=Number(-1),
                ),
            ]
        )
    )


def test_divide_multivariate():
    assert AST("(3n + 3c)/(n+c)").eval() == Term(Number(3))
    assert AST("(a^3 + b^3)/(a + b)").eval() == Term(
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

    assert AST("(-3.75c^2 + 18ab + 4.5abc - 15c)/(3+0.75c)").eval() == Term(
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
    assert AST("(ab/(x + 5))*((x+5)(x-4)/cd)").eval() == Term(
        value=Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(
                                value=Product(
                                    [
                                        Term(value=Variable("a")),
                                        Term(value=Variable("b")),
                                        Term(value=Variable("x")),
                                    ]
                                )
                            ),
                            Term(
                                Number(-4),
                                Product(
                                    [
                                        Term(value=Variable("a")),
                                        Term(value=Variable("b")),
                                    ]
                                ),
                            ),
                        ]
                    )
                ),
                Term(
                    value=Product(
                        [
                            Term(value=Variable("c"), exp=Number(-1)),
                            Term(value=Variable("d"), exp=Number(-1)),
                        ]
                    ),
                ),
            ]
        )
    )


def test_multiply_polynomial():
    # Multiplying univariate polynomials
    assert AST("(2x+3)(0.5x - 5)").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(-17, 2), Variable("x")),
                Term(Number(-15)),
            ]
        )
    )
    assert AST("(x + 1)(x + 2)(x + 3)").eval() == Term(
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
    assert AST("(x + 1)(y + 2)").eval() == Term(
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
    assert AST("(x - 4 + 12/(x + 4))(x+4)").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(-4)),
            ]
        )
    )
    # Nested
    assert AST("((z + 3)(z - 3))^2").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(4)),
                Term(Number(-18), Variable("z"), Number(2)),
                Term(Number(81)),
            ]
        )
    )
    # Negative Exponents
    assert AST("(x+1)^-1(x^2+2x+1)").eval() == Term(
        value=Polynomial(
            [
                Term(value=Variable("x")),
                Term(Number(1)),
            ]
        )
    )

    assert AST("(x/3 - 7/3)x^-2").eval() == Term(
        Number(1, 3),
        value=Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(-7)),
                        ]
                    )
                ),
                Term(value=Variable("x"), exp=Number(-2)),
            ]
        ),
    )
    # Consinstency regardless of the order
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
    assert AST("(x+2)^-1(3x-4)(xy+2y)").eval() == expected
    assert AST("(3x-4)(x+2)^-1(xy+2y)").eval() == expected
    assert AST("(xy+2y)(3x-4)(x+2)^-1").eval() == expected


def test_multiply_rationals():
    # Multiplying Polynomial rationals
    assert AST(
        "((x^4 - 25x^2)/(x^2 + 8x + 15)) * ((x^2 + 2x - 3)/(6x^3 - 36x^2 + 30x))"
    ).eval() == Term(Number(1, 6), Variable("x"))
    assert AST(
        "((2x^4 - 8x^2)/(x^4 - 10x^3)) * ((x + 7)/(4x^2 + 36x + 56))"
    ).eval() == Term(
        value=Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(-2)),
                        ]
                    )
                ),
                Term(
                    value=Polynomial(
                        [
                            Term(Number(2), Variable("x"), Number(2)),
                            Term(Number(-20), Variable("x")),
                        ]
                    ),
                    exp=Number(-1),
                ),
            ]
        )
    )
    assert AST(
        "((x^3 - 6x^2 - 7x)/(3x + 27)) * ((x^2 - 81)/(x^5 - 8x^4 - 9x^3))"
    ).eval() == Term(
        Number(1, 3),
        Product(
            [
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(-7)),
                        ]
                    )
                ),
                Term(value=Variable("x"), exp=Number(-2)),
            ]
        ),
    )

    assert AST(
        ("((x^2 - 49)/(x^2 + x - 56)) * ((6x^4 - 54x^3)/(2x^4 - 4x^3 - 126x^2))")
    ).eval() == Term(
        Number(3),
        Product(
            [
                Term(value=Variable("x")),
                Term(
                    value=Polynomial(
                        [
                            Term(value=Variable("x")),
                            Term(Number(8)),
                        ]
                    ),
                    exp=Number(-1),
                ),
            ]
        ),
    )
    assert AST(("(x^2-25)/((x-5)/(x+10))")).eval() == Term(
        value=Polynomial(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(Number(15), Variable("x")),
                Term(Number(50)),
            ]
        ),
    )

    assert AST(
        "-9x/(x^2 - 8x) * (9x^3 + 36x^2 - 189x)/(x^2 - 10x + 21) / ((x + 7)/(x^2 - 15x + 56))"
    ).eval() == Term(Number(-81), Variable("x"))
    assert AST(
        "(24 - 6x)/(x^2 - 10x + 24) * (x^2 - 8x + 12)/(10 - x) / ((x^2 + 8x - 20)/(100x - x^3))"
    ).eval() == Term(Number(-6), Variable("x"))
    assert AST(
        "(-x - 6)/(x + 9) * (x + 10)/(-2x - 18) / ((x^2 + 16x + 60)/(x^2 + 18x + 81))"
    ).eval() == Term(Number(1, 2))

    # fmt:off
    assert AST("((x^2 - 4)/(x^2 + 4x + 4)) * ((x^3 + 8)/(x^3 - 2x^2 - 4x + 8))").eval()==Term(
        value=Product([
                    Term(value=Polynomial([
                                Term(value=Variable("x"),exp=Number(2)),
                                Term(Number(-2),Variable("x")),
                                Term(Number(4)),
                    ])),
                    Term(value=Polynomial([
                                Term(value=Variable("x"),exp=Number(2)),
                                Term(Number(-4)),
                            ]),
                        exp=Number(-1)
                    )])
    )
    # fmt:on


@pytest.mark.skip
def test_add_rationals():
    # fmt:off
    assert AST("((x-y)/(x+y))^2 + ((x+y)/(x-y))^2").eval()==Term(
        value=Polynomial([
        Term(Number(2)),
        Term(Number(16),
            Product([
                Term(value=Variable("x"),exp=Number(2)),
                Term(value=Variable("y"),exp=Number(2)),
                Term(value=Polynomial([
                        Term(value=Variable("y"),exp=Number(4)),
                        Term(value=Variable("x"),exp=Number(4)),
                        Term(Number(-2),
                            Product([
                                Term(value=Variable("x"),exp=Number(2)),
                                Term(value=Variable("y"),exp=Number(2)),
                        ])),
                    ]),
                    exp=Number(-1))
        ]))
    ]))
    # fmt:on


def test_merge_polynomial():
    assert AST("(x^2 + 2x + 1) - (x + 1)").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(1), Variable("x")),
            ]
        )
    )
    assert AST("(z^2 + 4z + 3) - (z + 3)").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("z"), Number(2)),
                Term(Number(3), Variable("z")),
            ]
        )
    )
    assert AST("2x^2 + 3x - 5 + x^2 - x + 4").eval() == Term(
        value=Polynomial(
            [
                Term(Number(3), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(Number(-1)),
            ]
        )
    )
    assert AST("3y^2 + 4y - 6 + y^2 - y + 5").eval() == Term(
        value=Polynomial(
            [
                Term(Number(4), Variable("y"), Number(2)),
                Term(Number(3), Variable("y")),
                Term(Number(-1)),
            ]
        )
    )
    assert AST("2(2√(x + c)) - 1.5(2√(x + c))").eval() == Term(
        Number(1, 2),
        Polynomial(
            [
                Term(value=Variable("x")),
                Term(value=Variable("c")),
            ]
        ),
        Number(1, 2),
    )
    assert AST("3/x - 7/3x^2").eval() == Term(
        Number(1, 3),
        Product(
            [
                Term(
                    value=Polynomial([Term(Number(9), Variable("x")), Term(Number(-7))])
                ),
                Term(value=Variable("x"), exp=Number(-2)),
            ]
        ),
    )
