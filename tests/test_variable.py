from processing import AST
from data_types import Number, Variable, Term, Polynomial, Product


def test_merge_like_terms(interpreter):
    assert interpreter.eval(AST("2x + 3x")) == Term(Number(5), Variable("x"))
    assert interpreter.eval(AST("4y + 2y")) == Term(Number(6), Variable("y"))
    assert interpreter.eval(AST("5z - 3z")) == Term(Number(2), Variable("z"))


def test_divide_variables(interpreter):
    assert interpreter.eval(AST("x^2 / x")) == Term(Number(1), Variable("x"), Number(1))
    assert interpreter.eval(AST("z^4 / z^2")) == Term(
        Number(1), Variable("z"), Number(2)
    )
    assert interpreter.eval(AST("x^2 / y^2")) == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(-2)),
            ]
        )
    )


def test_multiply_variables(interpreter):
    assert interpreter.eval(AST("2x * 3x")) == Term(Number(6), Variable("x"), Number(2))
    assert interpreter.eval(AST("4y * 8z")) == Term(
        Number(32), Product([Term(value=Variable("y")), Term(value=Variable("z"))])
    )


def test_handle_exponents(interpreter):
    assert interpreter.eval(AST("x^2 * x^3")) == Term(
        Number(1),
        Variable("x"),
        Number(5),
    )
    assert interpreter.eval(AST("(x^2)^y")) == Term(
        value=Variable("x"), exp=Term(Number(2), Variable("y"))
    )
    assert interpreter.eval(AST("x^a * x^b")) == Term(
        Number(1),
        Variable("x"),
        Term(value=Polynomial([Term(value=Variable("a")), Term(value=Variable("b"))])),
    )
    assert interpreter.eval(AST("z^p / z^q")) == Term(
        Number(1),
        Variable("z"),
        Term(
            value=Polynomial(
                [Term(value=Variable("p")), Term(coef=Number(-1), value=Variable("q"))]
            )
        ),
    )
    assert interpreter.eval(AST("z^(6/8)")) == Term(
        Number(1), Variable("z"), Number("3/4")
    )
    assert interpreter.eval(AST("x^-2")) == Term(Number(1), Variable("x"), Number(-2))
    assert interpreter.eval(AST("y^0")) == Term()
    assert interpreter.eval(AST("12^0")) == Term()
    assert interpreter.eval(AST("0^0")) == Term()
