from data_types import *
from processing import AST


def test_solve_basic(interpreter):
    assert Equation(interpreter.eval(AST("5x+3")), AlgebraObject(Number(13)))[
        Variable("x")
    ].right == AlgebraObject(Number(2))

    assert Equation(interpreter.eval(AST("2x-7")), AlgebraObject(Number(3)))[
        Variable("x")
    ].right == AlgebraObject(Number(5))

    assert Equation(interpreter.eval(AST("x/4")), AlgebraObject(Number(5)))[
        Variable("x")
    ].right == AlgebraObject(Number(20))

    assert Equation(interpreter.eval(AST("x+6")), interpreter.eval(AST("2x-4")))[
        Variable("x")
    ].right == AlgebraObject(Number(10))


def test_solve_medium(interpreter):
    assert Equation(interpreter.eval(AST("3(x+2)")), AlgebraObject(Number(15)))[
        Variable("x")
    ].right == AlgebraObject(Number(3))

    assert Equation(interpreter.eval(AST("(2x+1)/3")), AlgebraObject(Number(5)))[
        Variable("x")
    ].right == AlgebraObject(Number(7))

    assert Equation(interpreter.eval(AST("2/x")), AlgebraObject(Number(8)))[
        Variable("x")
    ].right == AlgebraObject(Number("0.25"))

    assert Equation(interpreter.eval(AST("4x-3")), interpreter.eval(AST("2(x+5)")))[
        Variable("x")
    ].right == AlgebraObject(Number("6.5"))

    assert Equation(interpreter.eval(AST("3x+2y-7")), interpreter.eval(AST("5y+4")))[
        Variable("x")
    ].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("y")),
                AlgebraObject(Number("11/3")),
            ]
        )
    )
    assert Equation(
        interpreter.eval(AST("(4x-5)/3 + 7x/2")), AlgebraObject(Number("11/6"))
    )[Variable("x")].right == AlgebraObject(value=Number("21/29"))

    assert Equation(interpreter.eval(AST("2x+3y-z")), AlgebraObject(Number(0)))[
        Variable("x")
    ].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number("0.5"), Variable("z")),
                AlgebraObject(Number("-1.5"), Variable("y")),
            ]
        )
    )

    assert Equation(interpreter.eval(AST("(x-3)/(x+2)")), AlgebraObject(Number(4)))[
        Variable("x")
    ].right == AlgebraObject(Number("-11/3"))


def test_solve_formulas(interpreter):
    assert Equation(
        interpreter.eval(AST("a^2+b^2")),
        AlgebraObject(value=Variable("c"), exp=Number(2)),
    )[Variable("b")].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("c"), exp=Number(2)),
                AlgebraObject(Number(-1), Variable("a"), exp=Number(2)),
            ]
        ),
        exp=Number("0.5"),
    )

    assert Equation(AlgebraObject(value=Variable("d")), interpreter.eval(AST("st")))[
        Variable("t")
    ].right == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Variable("d")),
                AlgebraObject(value=Variable("s"), exp=Number(-1)),
            ]
        ),
    )

    assert Equation(AlgebraObject(value=Variable("I")), interpreter.eval(AST("Prt")))[
        Variable("P")
    ].right == AlgebraObject(
        value=Product(
            [
                AlgebraObject(value=Variable("I")),
                AlgebraObject(value=Variable("r"), exp=Number(-1)),
                AlgebraObject(value=Variable("t"), exp=Number(-1)),
            ]
        ),
    )

    assert Equation(
        interpreter.eval(AST("ax + b")), AlgebraObject(value=Variable("c"))
    )[Variable("b")].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("c")),
                AlgebraObject(
                    Number(-1),
                    Product(
                        [
                            AlgebraObject(value=Variable("a")),
                            AlgebraObject(value=Variable("x")),
                        ]
                    ),
                ),
            ]
        ),
    )
