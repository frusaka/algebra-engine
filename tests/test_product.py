from processing import AST
from data_types import Number, Variable, Term, Product, Polynomial


def test_divide_products(interpreter):
    assert interpreter.eval(AST("8x / 12x^2b")) == Term(
        Number("2/3"),
        Product(
            [
                Term(value=Variable("x"), exp=Number(-1)),
                Term(value=Variable("b"), exp=Number(-1)),
            ]
        ),
    )
    assert interpreter.eval(AST("5x^2b / 10axb")) == Term(
        Number("1/2"),
        Product(
            [
                Term(value=Variable("x")),
                Term(value=Variable("a"), exp=Number(-1)),
            ]
        ),
    )
    assert interpreter.eval(AST("6ab / 8a")) == Term(Number("3/4"), Variable("b"))
    assert interpreter.eval(AST("3ab / 0.1b")) == Term(Number(30), Variable("a"))
    assert interpreter.eval(AST("6ab / 8ab")) == Term(Number("3/4"))


def test_multiply_products(interpreter):
    assert interpreter.eval(AST("(2xy)^2")) == Term(
        Number(4),
        Product(
            [
                Term(value=Variable("x"), exp=Number(2)),
                Term(value=Variable("y"), exp=Number(2)),
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
    assert interpreter.eval(AST("3x^2b * 0.1ax^2")) == Term(
        Number("3/10"),
        Product(
            [
                Term(value=Variable("a")),
                Term(value=Variable("b")),
                Term(value=Variable("x"), exp=Number(4)),
            ]
        ),
    )
    assert interpreter.eval(AST("3xab(3ay-12b)")) == Term(
        value=Polynomial(
            [
                Term(
                    Number(9),
                    value=Product(
                        [
                            Term(value=Variable("a"), exp=Number(2)),
                            Term(value=Variable("b")),
                            Term(value=Variable("x")),
                            Term(value=Variable("y")),
                        ]
                    ),
                ),
                Term(
                    Number(-36),
                    value=Product(
                        [
                            Term(value=Variable("b"), exp=Number(2)),
                            Term(value=Variable("x")),
                            Term(value=Variable("a")),
                        ]
                    ),
                ),
            ]
        ),
    )
