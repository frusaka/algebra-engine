from processing import AST
from data_types import Number, Variable, AlgebraObject, Polynomial, Product


def test_merge_like_terms(interpreter):
    assert interpreter.eval(AST("2x + 3x")) == AlgebraObject(Number(5), Variable("x"))
    assert interpreter.eval(AST("4y + 2y")) == AlgebraObject(Number(6), Variable("y"))
    assert interpreter.eval(AST("5z - 3z")) == AlgebraObject(Number(2), Variable("z"))


def test_divide_variables(interpreter):
    assert interpreter.eval(AST("x^2 / x")) == AlgebraObject(
        Number(1), Variable("x"), Number(1)
    )
    assert interpreter.eval(AST("z^4 / z^2")) == AlgebraObject(
        Number(1), Variable("z"), Number(2)
    )
    assert interpreter.eval(AST("x^2 / y^2")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Variable("x"), exp=Number(2)),
                AlgebraObject(value=Variable("y"), exp=Number(-2)),
            ]
        )
    )


def test_multiply_variables(interpreter):
    assert interpreter.eval(AST("2x * 3x")) == AlgebraObject(
        Number(6), Variable("x"), Number(2)
    )
    assert interpreter.eval(AST("4y * 8z")) == AlgebraObject(
        Number(32),
        Product(
            [AlgebraObject(value=Variable("y")), AlgebraObject(value=Variable("z"))]
        ),
    )
