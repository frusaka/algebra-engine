import pytest
from datatypes.nodes import Const, Var, Add, Mul


def test_variable_exponent_number(processor):
    assert processor.eval("2^x") == Term(value=Const(2), exp=Term(value=Var("x")))
    assert processor.eval("4^-x") == Term(value=Const(1, 4), exp=Term(value=Var("x")))
    assert processor.eval("3^(2f)") == Term(value=Const(9), exp=Term(value=Var("f")))
    assert processor.eval("(3^(2f))^0.5") == Term(
        value=Const(3), exp=Term(value=Var("f"))
    )
    assert processor.eval("3^a + 3^a") == Term(Const(2), Const(3), Term(value=Var("a")))
    assert processor.eval("0.5(5^x)+5^x") == Term(
        Const(3, 2), Const(5), Term(value=Var("x"))
    )
    assert processor.eval("2.5^p * 4^p") == Term(
        value=Const(10), exp=Term(value=Var("p"))
    )
    assert processor.eval("(3^x)^2 / 9^x") == Term(Const(1))
    assert processor.eval("3^x * 3^y") == Term(
        value=Const(3),
        exp=Term(value=Add([Term(value=Var("x")), Term(value=Var("y"))])),
    )


def test_polynomial_exponentiation(processor):
    # Needs more cases
    assert processor.eval("(x + 1)^2") == Term(
        value=Add(
            [
                Term(Const(1), Var("x"), Const(2)),
                Term(Const(2), Var("x")),
                Term(),
            ]
        )
    )


def test_variable_exponentiation(processor):
    assert processor.eval("x^2 * x^3") == Term(
        Const(1),
        Var("x"),
        Const(5),
    )
    assert processor.eval("(x^2)^y") == Term(
        value=Var("x"), exp=Term(Const(2), Var("y"))
    )
    assert processor.eval("x^a * x^b") == Term(
        Const(1),
        Var("x"),
        Term(value=Add([Term(value=Var("a")), Term(value=Var("b"))])),
    )
    assert processor.eval("(5x^-2)^(2n) * (x^3)^(3n)") == Term(
        value=Mul(
            [
                Term(value=Const(25), exp=Term(value=Var("n"))),
                Term(value=Var("x"), exp=Term(Const(5), Var("n"))),
            ]
        )
    )
    assert processor.eval("(4/x^2)^(3n)") == Term(
        value=Mul(
            [
                Term(value=Const(64), exp=Term(value=Var("n"))),
                Term(value=Var("x"), exp=Term(Const(-6), Var("n"))),
            ]
        )
    )
    assert processor.eval("(2x^3)^(2y)*(x^2)^(3z)") == Term(
        value=Mul(
            [
                Term(value=Const(4), exp=Term(value=Var("y"))),
                Term(
                    value=Var("x"),
                    exp=Term(
                        value=Add(
                            [
                                Term(Const(6), Var("z")),
                                Term(Const(6), Var("y")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
    assert processor.eval("z^p / z^q") == Term(
        Const(1),
        Var("z"),
        Term(
            value=Add(
                [
                    Term(value=Var("p")),
                    Term(coef=Const(-1), value=Var("q")),
                ]
            )
        ),
    )
    assert processor.eval("(6x^2)^n / (3x)^(2n)") == Term(
        value=Const(2, 3), exp=Term(value=Var("n"))
    )
    assert processor.eval("z^(6/8)") == Term(Const(1), Var("z"), Const(3, 4))
    assert processor.eval("x^-2") == Term(Const(1), Var("x"), Const(-2))
    # Edge cases
    assert processor.eval("y^0") == Term()
    assert processor.eval("0^0") == Term()
    assert processor.eval("0^j") == Term(Const(0))


def test_polynomial_exponent(processor):
    assert processor.eval("1/23 * (3^(1-2^0.5))^(1+2^0.5)") == Term(Const(1, 69))
    assert processor.eval("x^(f+2)/x^2") == Term(
        value=Var("x"), exp=Term(value=Var("f"))
    )
    assert processor.eval("(4y)^(n-1)/(4y)^n") == Term(Const(1, 4), Var("y"), Const(-1))
    # assert processor.eval("(3y^2)^(2x) / (3^(x+1)*y^x)")
    assert processor.eval("(4z)^(n-2) / (4z)^(n+1)") == Term(
        Const(1, 64), Var("z"), Const(-3)
    )
    assert processor.eval("(a^b/c^d)^(m+1)") == Term(
        value=Mul(
            [
                Term(
                    value=Var("a"),
                    exp=Term(
                        value=Add(
                            [
                                Term(
                                    value=Mul(
                                        [
                                            Term(value=Var("b")),
                                            Term(value=Var("m")),
                                        ]
                                    )
                                ),
                                Term(value=Var("b")),
                            ]
                        )
                    ),
                ),
                Term(
                    value=Var("c"),
                    exp=Term(
                        value=Add(
                            [
                                Term(
                                    Const(-1),
                                    Mul(
                                        [
                                            Term(value=Var("d")),
                                            Term(value=Var("m")),
                                        ]
                                    ),
                                ),
                                Term(Const(-1), Var("d")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
