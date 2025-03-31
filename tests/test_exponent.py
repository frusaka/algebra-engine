import pytest
from datatypes import Term, Number, Variable, Polynomial, Product
from processing import AST


def test_variable_exponent_number():
    assert AST("2^x").eval() == Term(value=Number(2), exp=Term(value=Variable("x")))
    assert AST("4^-x").eval() == Term(value=Number(1, 4), exp=Term(value=Variable("x")))
    assert AST("3^(2f)").eval() == Term(value=Number(9), exp=Term(value=Variable("f")))
    assert AST("(3^(2f))^0.5").eval() == Term(
        value=Number(3), exp=Term(value=Variable("f"))
    )
    assert AST("3^a + 3^a").eval() == Term(
        Number(2), Number(3), Term(value=Variable("a"))
    )
    assert AST("0.5(5^x)+5^x").eval() == Term(
        Number(3, 2), Number(5), Term(value=Variable("x"))
    )
    assert AST("2.5^p * 4^p").eval() == Term(
        value=Number(10), exp=Term(value=Variable("p"))
    )
    assert AST("(3^x)^2 / 9^x").eval() == Term(Number(1))
    assert AST("3^x * 3^y").eval() == Term(
        value=Number(3),
        exp=Term(
            value=Polynomial([Term(value=Variable("x")), Term(value=Variable("y"))])
        ),
    )


def test_polynomial_exponentiation():
    # Needs more cases
    assert AST("(x + 1)^2").eval() == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(),
            ]
        )
    )


def test_variable_exponentiation():
    assert AST("x^2 * x^3").eval() == Term(
        Number(1),
        Variable("x"),
        Number(5),
    )
    assert AST("(x^2)^y").eval() == Term(
        value=Variable("x"), exp=Term(Number(2), Variable("y"))
    )
    assert AST("x^a * x^b").eval() == Term(
        Number(1),
        Variable("x"),
        Term(value=Polynomial([Term(value=Variable("a")), Term(value=Variable("b"))])),
    )
    assert AST("(5x^-2)^(2n) * (x^3)^(3n)").eval() == Term(
        value=Product(
            [
                Term(value=Number(25), exp=Term(value=Variable("n"))),
                Term(value=Variable("x"), exp=Term(Number(5), Variable("n"))),
            ]
        )
    )
    assert AST("(4/x^2)^(3n)").eval() == Term(
        value=Product(
            [
                Term(value=Number(64), exp=Term(value=Variable("n"))),
                Term(value=Variable("x"), exp=Term(Number(-6), Variable("n"))),
            ]
        )
    )
    assert AST("(2x^3)^(2y)*(x^2)^(3z)").eval() == Term(
        value=Product(
            [
                Term(value=Number(4), exp=Term(value=Variable("y"))),
                Term(
                    value=Variable("x"),
                    exp=Term(
                        value=Polynomial(
                            [
                                Term(Number(6), Variable("z")),
                                Term(Number(6), Variable("y")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
    assert AST("z^p / z^q").eval() == Term(
        Number(1),
        Variable("z"),
        Term(
            value=Polynomial(
                [
                    Term(value=Variable("p")),
                    Term(coef=Number(-1), value=Variable("q")),
                ]
            )
        ),
    )
    assert AST("(6x^2)^n / (3x)^(2n)").eval() == Term(
        value=Number(2, 3), exp=Term(value=Variable("n"))
    )
    assert AST("z^(6/8)").eval() == Term(Number(1), Variable("z"), Number(3, 4))
    assert AST("x^-2").eval() == Term(Number(1), Variable("x"), Number(-2))
    # Edge cases
    assert AST("y^0").eval() == Term()
    assert AST("0^0").eval() == Term()
    assert AST("0^j").eval() == Term(Number(0))


def test_polynomial_exponent():
    assert AST("4^f*4").eval() == Term(
        value=Number(4),
        exp=Term(value=Polynomial([Term(value=Variable("f")), Term(value=Number(1))])),
    )
    assert AST("x^(f+2)/x^2").eval() == Term(
        value=Variable("x"), exp=Term(value=Variable("f"))
    )
    assert AST("(4y)^(n-1)/(4y)^n").eval() == Term(
        Number(1, 4), Variable("y"), Number(-1)
    )
    # assert AST("(3y^2)^(2x) / (3^(x+1)*y^x)").eval()
    assert AST("(4z)^(n-2) / (4z)^(n+1)").eval() == Term(
        Number(1, 64), Variable("z"), Number(-3)
    )
    assert AST("(a^b/c^d)^(m+1)").eval() == Term(
        value=Product(
            [
                Term(
                    value=Variable("a"),
                    exp=Term(
                        value=Polynomial(
                            [
                                Term(
                                    value=Product(
                                        [
                                            Term(value=Variable("b")),
                                            Term(value=Variable("m")),
                                        ]
                                    )
                                ),
                                Term(value=Variable("b")),
                            ]
                        )
                    ),
                ),
                Term(
                    value=Variable("c"),
                    exp=Term(
                        value=Polynomial(
                            [
                                Term(
                                    Number(-1),
                                    Product(
                                        [
                                            Term(value=Variable("d")),
                                            Term(value=Variable("m")),
                                        ]
                                    ),
                                ),
                                Term(Number(-1), Variable("d")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
