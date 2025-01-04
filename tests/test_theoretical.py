import pytest
from processing import AST
from data_types import Term, Number, Variable, Polynomial


@pytest.mark.xfail(reason="Feature under development")
def test_number_variable_exponent(interpreter):
    assert interpreter.eval(AST("2^x")) == Term(
        value=Number(2), exp=Term(value=Variable("x"))
    )
    assert interpreter.eval(AST("4^-x")) == Term(
        value=Number("1/4"), exp=Term(value=Variable("x"))
    )
    assert interpreter.eval(AST("3^(2f)")) == Term(
        value=Number(9), exp=Term(value=Variable("f"))
    )
    assert interpreter.eval(AST("(3^(2f))^0.5")) == Term(
        value=Number(3), exp=Term(value=Variable("f"))
    )
