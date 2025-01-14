import pytest
from processing import AST
from data_types import AlgebraObject, Number, Variable, Polynomial, Product


def test_variable_exponent_number(interpreter):
    assert interpreter.eval(AST("2^x")) == AlgebraObject(
        value=Number(2), exp=AlgebraObject(value=Variable("x"))
    )
    assert interpreter.eval(AST("4^-x")) == AlgebraObject(
        value=Number("1/4"), exp=AlgebraObject(value=Variable("x"))
    )
    assert interpreter.eval(AST("3^(2f)")) == AlgebraObject(
        value=Number(9), exp=AlgebraObject(value=Variable("f"))
    )
    assert interpreter.eval(AST("(3^(2f))^0.5")) == AlgebraObject(
        value=Number(3), exp=AlgebraObject(value=Variable("f"))
    )
    assert interpreter.eval(AST("3^a + 3^a")) == AlgebraObject(
        Number(2), Number(3), AlgebraObject(value=Variable("a"))
    )
    assert interpreter.eval(AST("0.5(5^x)+5^x")) == AlgebraObject(
        Number("1.5"), Number(5), AlgebraObject(value=Variable("x"))
    )
    assert interpreter.eval(AST("2.5^p * 4^p")) == AlgebraObject(
        value=Number(10), exp=AlgebraObject(value=Variable("p"))
    )
    assert interpreter.eval(AST("(3^x)^2 / 9^x")) == AlgebraObject(Number(1))
    assert interpreter.eval(AST("3^x * 3^y")) == AlgebraObject(
        value=Number(3),
        exp=AlgebraObject(
            value=Polynomial(
                [AlgebraObject(value=Variable("x")), AlgebraObject(value=Variable("y"))]
            )
        ),
    )


def test_polynomial_exponentiation(interpreter):
    # Needs more cases
    assert interpreter.eval(AST("(x + 1)^2")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(1), Variable("x"), Number(2)),
                AlgebraObject(Number(2), Variable("x")),
                AlgebraObject(),
            ]
        )
    )


def test_variable_exponentiation(interpreter):
    assert interpreter.eval(AST("x^2 * x^3")) == AlgebraObject(
        Number(1),
        Variable("x"),
        Number(5),
    )
    assert interpreter.eval(AST("(x^2)^y")) == AlgebraObject(
        value=Variable("x"), exp=AlgebraObject(Number(2), Variable("y"))
    )
    assert interpreter.eval(AST("x^a * x^b")) == AlgebraObject(
        Number(1),
        Variable("x"),
        AlgebraObject(
            value=Polynomial(
                [AlgebraObject(value=Variable("a")), AlgebraObject(value=Variable("b"))]
            )
        ),
    )
    assert interpreter.eval(AST("(5x^-2)^(2n) * (x^3)^(3n)")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Number(25), exp=AlgebraObject(value=Variable("n"))),
                AlgebraObject(
                    value=Variable("x"), exp=AlgebraObject(Number(5), Variable("n"))
                ),
            ]
        )
    )
    assert interpreter.eval(AST("(4/x^2)^(3n)")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Number(64), exp=AlgebraObject(value=Variable("n"))),
                AlgebraObject(
                    value=Variable("x"), exp=AlgebraObject(Number(-6), Variable("n"))
                ),
            ]
        )
    )
    assert interpreter.eval(AST("(2x^3)^(2y)*(x^2)^(3z)")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Number(4), exp=AlgebraObject(value=Variable("y"))),
                AlgebraObject(
                    value=Variable("x"),
                    exp=AlgebraObject(
                        value=Polynomial(
                            [
                                AlgebraObject(Number(6), Variable("z")),
                                AlgebraObject(Number(6), Variable("y")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
    assert interpreter.eval(AST("z^p / z^q")) == AlgebraObject(
        Number(1),
        Variable("z"),
        AlgebraObject(
            value=Polynomial(
                [
                    AlgebraObject(value=Variable("p")),
                    AlgebraObject(coef=Number(-1), value=Variable("q")),
                ]
            )
        ),
    )
    assert interpreter.eval(AST("(6x^2)^n / (3x)^(2n)")) == AlgebraObject(
        value=Number("2/3"), exp=AlgebraObject(value=Variable("n"))
    )
    assert interpreter.eval(AST("z^(6/8)")) == AlgebraObject(
        Number(1), Variable("z"), Number("3/4")
    )
    assert interpreter.eval(AST("x^-2")) == AlgebraObject(
        Number(1), Variable("x"), Number(-2)
    )
    assert interpreter.eval(AST("y^0")) == AlgebraObject()


def test_polynomial_exponent(interpreter):
    assert interpreter.eval(AST("4^f*4")) == AlgebraObject(
        value=Number(4),
        exp=AlgebraObject(
            value=Polynomial(
                [AlgebraObject(value=Variable("f")), AlgebraObject(value=Number(1))]
            )
        ),
    )
    assert interpreter.eval(AST("x^(f+2)/x^2")) == AlgebraObject(
        value=Variable("x"), exp=AlgebraObject(value=Variable("f"))
    )
    assert interpreter.eval(AST("(4y)^(n-1)/(4y)^n")) == AlgebraObject(
        Number("0.25"), Variable("y"), Number(-1)
    )
    assert interpreter.eval(AST("(3y^2)^(2x) / (3^(x+1)*y^x)"))
    assert interpreter.eval(AST("(4z)^(n-2) / (4z)^(n+1)")) == AlgebraObject(
        Number("1/64"), Variable("z"), Number(-3)
    )
    assert interpreter.eval(AST("(a^b/c^d)^(m+1)")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(
                    value=Variable("a"),
                    exp=AlgebraObject(
                        value=Polynomial(
                            [
                                AlgebraObject(
                                    value=Product(
                                        [
                                            AlgebraObject(value=Variable("b")),
                                            AlgebraObject(value=Variable("m")),
                                        ]
                                    )
                                ),
                                AlgebraObject(value=Variable("b")),
                            ]
                        )
                    ),
                ),
                AlgebraObject(
                    value=Variable("c"),
                    exp=AlgebraObject(
                        value=Polynomial(
                            [
                                AlgebraObject(
                                    Number(-1),
                                    Product(
                                        [
                                            AlgebraObject(value=Variable("d")),
                                            AlgebraObject(value=Variable("m")),
                                        ]
                                    ),
                                ),
                                AlgebraObject(Number(-1), Variable("d")),
                            ]
                        )
                    ),
                ),
            ]
        )
    )
