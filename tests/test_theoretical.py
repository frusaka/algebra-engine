import pytest
from processing import AST
from data_types import AlgebraObject, Number, Variable, Polynomial


@pytest.mark.xfail(reason="Feature under development")
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
