from processing import AST
from data_types import Number, Variable, AlgebraObject, Product, Polynomial


def test_divide_products(interpreter):
    assert interpreter.eval(AST("8x / 12x^2b")) == AlgebraObject(
        Number("2/3"),
        Product(
            [
                AlgebraObject(value=Variable("x"), exp=Number(-1)),
                AlgebraObject(value=Variable("b"), exp=Number(-1)),
            ]
        ),
    )
    assert interpreter.eval(AST("5x^2b / 10axb")) == AlgebraObject(
        Number("1/2"),
        Product(
            [
                AlgebraObject(value=Variable("x")),
                AlgebraObject(value=Variable("a"), exp=Number(-1)),
            ]
        ),
    )
    assert interpreter.eval(AST("6ab / 8a")) == AlgebraObject(
        Number("3/4"), Variable("b")
    )
    assert interpreter.eval(AST("3ab / 0.1b")) == AlgebraObject(
        Number(30), Variable("a")
    )
    assert interpreter.eval(AST("6ab / 8ab")) == AlgebraObject(Number("3/4"))


def test_multiply_products(interpreter):
    assert interpreter.eval(AST("(2xy)^2")) == AlgebraObject(
        Number(4),
        Product(
            [
                AlgebraObject(value=Variable("x"), exp=Number(2)),
                AlgebraObject(value=Variable("y"), exp=Number(2)),
            ]
        ),
    )
    assert interpreter.eval(AST("x^3 * z^3")) == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Variable("x"), exp=Number(3)),
                AlgebraObject(value=Variable("z"), exp=Number(3)),
            ]
        )
    )
    assert interpreter.eval(AST("3x^2b * 0.1ax^2")) == AlgebraObject(
        Number("3/10"),
        Product(
            [
                AlgebraObject(value=Variable("a")),
                AlgebraObject(value=Variable("b")),
                AlgebraObject(value=Variable("x"), exp=Number(4)),
            ]
        ),
    )
    assert interpreter.eval(AST("3xab(3ay-12b)")) == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(
                    Number(9),
                    value=Product(
                        [
                            AlgebraObject(value=Variable("a"), exp=Number(2)),
                            AlgebraObject(value=Variable("b")),
                            AlgebraObject(value=Variable("x")),
                            AlgebraObject(value=Variable("y")),
                        ]
                    ),
                ),
                AlgebraObject(
                    Number(-36),
                    value=Product(
                        [
                            AlgebraObject(value=Variable("b"), exp=Number(2)),
                            AlgebraObject(value=Variable("x")),
                            AlgebraObject(value=Variable("a")),
                        ]
                    ),
                ),
            ]
        ),
    )
