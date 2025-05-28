from datatypes import Number, Variable, Term, Polynomial, Product
from processing import Interpreter


def test_merge_like_terms():
    assert Interpreter.eval("2x + 3x") == Term(Number(5), Variable("x"))
    assert Interpreter.eval("4y + 2y") == Term(Number(6), Variable("y"))
    assert Interpreter.eval("5z - 3z") == Term(Number(2), Variable("z"))


def test_divide_variables():
    assert Interpreter.eval("x^2 / x") == Term(Number(1), Variable("x"), Number(1))
    assert Interpreter.eval("z^4 / z^2") == Term(Number(1), Variable("z"), Number(2))
    assert Interpreter.eval("x^2 / y^2") == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(-2)),
            ]
        )
    )


def test_multiply_variables():
    assert Interpreter.eval("2x * 3x") == Term(Number(6), Variable("x"), Number(2))
    assert Interpreter.eval("4y * 8z") == Term(
        Number(32),
        Product([Term(value=Variable("y")), Term(value=Variable("z"))]),
    )
