import pytest
from datatypes import Number, Variable, Term, Product, Polynomial
from processing import AST


def test_divide_product():
    assert AST("8x / 12x^2b").eval() == Term(
        Number(2, 3),
        Product(
            [
                Term(value=Variable("x"), exp=Number(-1)),
                Term(value=Variable("b"), exp=Number(-1)),
            ]
        ),
    )
    assert AST("5x^2b / 10axb").eval() == Term(
        Number(1, 2),
        Product(
            [
                Term(value=Variable("x")),
                Term(value=Variable("a"), exp=Number(-1)),
            ]
        ),
    )
    assert AST("6ab / 8a").eval() == Term(Number(3, 4), Variable("b"))
    assert AST("3ab / 0.1b").eval() == Term(Number(30), Variable("a"))
    assert AST("6ab / 8ab").eval() == Term(Number(3, 4))


def test_multiply_product():
    assert AST("(2xy)^2").eval() == Term(
        Number(4),
        Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(2)),
            ]
        ),
    )
    assert AST("x^3 * z^3").eval() == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(3)),
                Term(value=Variable("z"), exp=Number(3)),
            ]
        )
    )
    assert AST("3x^2b * 0.1ax^2").eval() == Term(
        Number(3, 10),
        Product(
            [
                Term(value=Variable("a")),
                Term(value=Variable("b")),
                Term(value=Variable("x"), exp=Number(4)),
            ]
        ),
    )
    assert AST("3xab(3ay-12b)").eval() == Term(
        value=Polynomial(
            [
                Term(
                    Number(9),
                    value=Product(
                        [
                            Term(value=Variable("a"), exp=Number(2)),
                            Term(value=Variable("b")),
                            Term(value=Variable("x")),
                            Term(value=Variable("y")),
                        ]
                    ),
                ),
                Term(
                    Number(-36),
                    value=Product(
                        [
                            Term(value=Variable("b"), exp=Number(2)),
                            Term(value=Variable("x")),
                            Term(value=Variable("a")),
                        ]
                    ),
                ),
            ]
        ),
    )


@pytest.mark.skip(reason="Feature not implemented")
def test_simplify_product():
    assert AST("(x + f) / x^3 * 3x^2").eval() == Term(
        value=Polynomial(
            [
                Term(
                    Number(3),
                    value=Product(
                        [
                            Term(value=Variable("f")),
                            Term(value=Variable("x"), exp=Number(-1)),
                        ]
                    ),
                ),
                Term(Number(3)),
            ]
        )
    )
    assert AST("(3x - 21)/x^2 / 3").eval() == Term(
        value=Product(
            [
                Term(value=Polynomial([Term(value=Variable("x")), Term(Number(-7))])),
                Term(value=Variable("x"), exp=Number(-2)),
            ]
        )
    )

    assert AST("3(2√2)(1/(3√12))2(2√6)").eval() == Term(
        Number(2),
        Product(
            [
                Term(value=Number(3), exp=Number(1, 2)),
                Term(value=Number(18), exp=Number(1, 3)),
            ]
        ),
    )
