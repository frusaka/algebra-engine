from datatypes import Number, Variable, Term, Product
from processing import AST

def test_merge_like_terms():
    assert AST("2x + 3x").eval() == Term(Number(5), Variable("x"))
    assert AST("4y + 2y").eval() == Term(Number(6), Variable("y"))
    assert AST("5z - 3z").eval() == Term(Number(2), Variable("z"))


def test_divide_variables():
    assert AST("x^2 / x").eval() == Term(Number(1), Variable("x"), Number(1))
    assert AST("z^4 / z^2").eval() == Term(Number(1), Variable("z"), Number(2))
    assert AST("x^2 / y^2").eval() == Term(
        value=Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(-2)),
            ]
        )
    )


def test_multiply_variables():
    assert AST("2x * 3x").eval() == Term(Number(6), Variable("x"), Number(2))
    assert AST("4y * 8z").eval() == Term(
        Number(32),
        Product([Term(value=Variable("y")), Term(value=Variable("z"))]),
    )
