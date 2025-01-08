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

    assert Equation(interpreter.eval(AST("3x^2")), interpreter.eval(AST("9 + 2x^2")))[
        Variable("x")
    ].right == AlgebraObject(Number(3))
    eq = Equation(interpreter.eval(AST("(3/x)y + 4")), AlgebraObject(Number(9)))
    assert eq[Variable("x")].right == AlgebraObject(Number("0.6"), Variable("y"))
    assert eq[Variable("y")].right == AlgebraObject(Number("5/3"), Variable("x"))


def test_solve_denominator(interpreter):
    eq = Equation(interpreter.eval(AST("3/c + n/c")), interpreter.eval(AST("8")))
    assert eq[Variable("c")].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number("0.125"), Variable("n")),
                AlgebraObject(Number("0.375")),
            ]
        )
    )
    assert eq[Variable("n")].right == AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(Number(8), Variable("c")),
                AlgebraObject(Number(-3)),
            ]
        )
    )
    eq = Equation(
        interpreter.eval(AST("4u - 5/j")), interpreter.eval(AST("u/j - 20"))
    )
    assert eq[Variable("j")].right == AlgebraObject(Number("0.25"))


def test_solve_factorization(interpreter):
    eq = Equation(
        interpreter.eval(AST("n(2-3b) + 2 - 4b")), interpreter.eval(AST("2b - 2"))
    )
    assert eq[Variable("n")].right == AlgebraObject(Number(-2))
    assert eq[Variable("b")].right == AlgebraObject(Number("2/3"))
    eq = Equation(
        interpreter.eval(AST("1.5y(3x-6) + 3x - 5")), interpreter.eval(AST("x - 1"))
    )
    assert eq[Variable("y")].right == AlgebraObject(Number("-4/9"))
    assert eq[Variable("x")].right == AlgebraObject(Number(2))


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
