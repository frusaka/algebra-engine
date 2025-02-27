import pytest
from datatypes import Term, Number, Variable, Polynomial, Product


def test_variable_exponent_number(processor):
    assert processor.eval("2^x") == Term(value=Number(2), exp=Term(value=Variable("x")))
    assert processor.eval("4^-x") == Term(
        value=Number(1, 4), exp=Term(value=Variable("x"))
    )
    assert processor.eval("3^(2f)") == Term(
        value=Number(9), exp=Term(value=Variable("f"))
    )
    assert processor.eval("(3^(2f))^0.5") == Term(
        value=Number(3), exp=Term(value=Variable("f"))
    )
    assert processor.eval("3^a + 3^a") == Term(
        Number(2), Number(3), Term(value=Variable("a"))
    )
    assert processor.eval("0.5(5^x)+5^x") == Term(
        Number(3, 2), Number(5), Term(value=Variable("x"))
    )
    assert processor.eval("2.5^p * 4^p") == Term(
        value=Number(10), exp=Term(value=Variable("p"))
    )
    assert processor.eval("(3^x)^2 / 9^x") == Term(Number(1))
    assert processor.eval("3^x * 3^y") == Term(
        value=Number(3),
        exp=Term(
            value=Polynomial([Term(value=Variable("x")), Term(value=Variable("y"))])
        ),
    )


def test_polynomial_exponentiation(processor):
    # Needs more cases
    assert processor.eval("(x + 1)^2") == Term(
        value=Polynomial(
            [
                Term(Number(1), Variable("x"), Number(2)),
                Term(Number(2), Variable("x")),
                Term(),
            ]
        )
    )


def test_variable_exponentiation(processor):
    assert processor.eval("x^2 * x^3") == Term(
        Number(1),
        Variable("x"),
        Number(5),
    )
    assert processor.eval("(x^2)^y") == Term(
        value=Variable("x"), exp=Term(Number(2), Variable("y"))
    )
    assert processor.eval("x^a * x^b") == Term(
        Number(1),
        Variable("x"),
        Term(value=Polynomial([Term(value=Variable("a")), Term(value=Variable("b"))])),
    )
    assert processor.eval("(5x^-2)^(2n) * (x^3)^(3n)") == Term(
        value=Product(
            [
                Term(value=Number(25), exp=Term(value=Variable("n"))),
                Term(value=Variable("x"), exp=Term(Number(5), Variable("n"))),
            ]
        )
    )
    assert processor.eval("(4/x^2)^(3n)") == Term(
        value=Product(
            [
                Term(value=Number(64), exp=Term(value=Variable("n"))),
                Term(value=Variable("x"), exp=Term(Number(-6), Variable("n"))),
            ]
        )
    )
    assert processor.eval("(2x^3)^(2y)*(x^2)^(3z)") == Term(
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
    assert processor.eval("z^p / z^q") == Term(
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
    assert processor.eval("(6x^2)^n / (3x)^(2n)") == Term(
        value=Number(2, 3), exp=Term(value=Variable("n"))
    )
    assert processor.eval("z^(6/8)") == Term(Number(1), Variable("z"), Number(3, 4))
    assert processor.eval("x^-2") == Term(Number(1), Variable("x"), Number(-2))
    assert processor.eval("y^0") == Term()


def test_polynomial_exponent(processor):
    assert processor.eval("4^f*4") == Term(
        value=Number(4),
        exp=Term(value=Polynomial([Term(value=Variable("f")), Term(value=Number(1))])),
    )
    assert processor.eval("x^(f+2)/x^2") == Term(
        value=Variable("x"), exp=Term(value=Variable("f"))
    )
    assert processor.eval("(4y)^(n-1)/(4y)^n") == Term(
        Number(1, 4), Variable("y"), Number(-1)
    )
    assert processor.eval("(3y^2)^(2x) / (3^(x+1)*y^x)")
    assert processor.eval("(4z)^(n-2) / (4z)^(n+1)") == Term(
        Number(1, 64), Variable("z"), Number(-3)
    )
    assert processor.eval("(a^b/c^d)^(m+1)") == Term(
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
