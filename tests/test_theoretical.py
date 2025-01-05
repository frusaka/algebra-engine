import pytest
from processing import AST
from data_types import AlgebraObject, Number, Variable, Polynomial


def test_number_variable_exponent(interpreter):
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


def test_number_arithmetic_with_variable_exponent(interpreter):
    assert interpreter.eval(AST("3^a + 3^a")) == AlgebraObject(
        Number(2), Number(3), AlgebraObject(value=Variable("a"))
    )
    assert interpreter.eval(AST("0.5(5^x)+5^x")) == AlgebraObject(
        Number("1.5"), Number(5), AlgebraObject(value=Variable("x"))
    )
    assert interpreter.eval(AST("4^z - 4^z")) == AlgebraObject(Number(0))
    assert interpreter.eval(AST("2*4^f")) == AlgebraObject(
        Number(2), Number(4), AlgebraObject(value=Variable("f"))
    )
    assert interpreter.eval(AST("4^a/2^a")) == AlgebraObject(
        value=Number(2), exp=AlgebraObject(value=Variable("a"))
    )
    assert interpreter.eval(AST("2.5^p * 4^p")) == AlgebraObject(
        value=Number(10), exp=AlgebraObject(value=Variable("p"))
    )
    assert interpreter.eval(AST("3^x * 3^y")) == AlgebraObject(
        value=Number(3),
        exp=AlgebraObject(
            value=Polynomial(
                [AlgebraObject(value=Variable("x")), AlgebraObject(value=Variable("y"))]
            )
        ),
    )
    assert interpreter.eval(AST("(3^x)^2 / 9^x")) == AlgebraObject(Number(1))
