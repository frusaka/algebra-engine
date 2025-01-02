import pytest
from processing import Interpreter, AST
from data_types import Number, Variable, Term, Product


@pytest.fixture
def interpreter():
    return Interpreter()


def test_divide_different_variables(interpreter):
    assert interpreter.eval(AST("x^2 / y^2")) == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(-2)),
            ]
        )
    )
    assert interpreter.eval(AST("x^3 / z^3")) == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(3)),
                Term(value=Variable("z"), exp=Number(-3)),
            ]
        )
    )


def test_multiply_variables(interpreter):
    assert interpreter.eval(AST("(2xy)^2")) == Term(
        Number(4),
        Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(2)),
            ]
        ),
    )
    assert interpreter.eval(AST("3ab*0.1b")) == Term(
        Number(3, 10),
        Product(
            [
                Term(value=Variable("a"), exp=Number(1)),
                Term(value=Variable("b"), exp=Number(2)),
            ]
        ),
    )
    assert interpreter.eval(AST("x^3 * z^3")) == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(3)),
                Term(value=Variable("z"), exp=Number(3)),
            ]
        )
    )
