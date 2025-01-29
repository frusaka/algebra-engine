import pytest
from data_types import *
from processing import AST


def test_solve_basic(processor):
    assert Equation(processor.eval(AST("5x+3")), AlgebraObject(Number(13)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(2))
    )

    assert Equation(processor.eval(AST("2x-7")), AlgebraObject(Number(3)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(5))
    )

    assert Equation(processor.eval(AST("x/4")), AlgebraObject(Number(5)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(20))
    )

    assert Equation(processor.eval(AST("x+6")), processor.eval(AST("2x-4")))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(10))
    )


def test_solve_medium(processor):
    assert Equation(processor.eval(AST("3(x+2)")), AlgebraObject(Number(15)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(3))
    )

    assert Equation(processor.eval(AST("(2x+1)/3")), AlgebraObject(Number(5)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(7))
    )

    assert Equation(processor.eval(AST("2/x")), AlgebraObject(Number(8)))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number("0.25"))
    )

    assert Equation(processor.eval(AST("4x-3")), right=processor.eval(AST("2(x+5)")))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number("6.5"))
    )

    assert Equation(processor.eval(AST("3x+2y-7")), processor.eval(AST("5y+4")))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=AlgebraObject(
            value=Polynomial(
                [
                    AlgebraObject(value=Variable("y")),
                    AlgebraObject(Number("11/3")),
                ]
            )
        ),
    )
    assert Equation(
        left=processor.eval(AST("(4x-5)/3 + 7x/2")),
        right=AlgebraObject(Number("11/6")),
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number("21/29"))
    )

    assert Equation(
        left=processor.eval(AST("2x+3y-z")), right=AlgebraObject(Number(0))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=AlgebraObject(
            value=Polynomial(
                [
                    AlgebraObject(Number("0.5"), Variable("z")),
                    AlgebraObject(Number("-1.5"), Variable("y")),
                ]
            )
        ),
    )

    assert Equation(
        left=processor.eval(AST("(x-3)/(x+2)")), right=AlgebraObject(Number(4))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number("-11/3"))
    )

    assert Equation(processor.eval(AST("3x^2")), processor.eval(AST("9 + 2x^2")))[
        Variable("x")
    ] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=Solutions({AlgebraObject(Number(3)), AlgebraObject(Number(-3))}),
    )
    eq = Equation(
        left=processor.eval(AST("(3/x)y + 4")), right=AlgebraObject(Number(9))
    )
    assert eq[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=AlgebraObject(Number("0.6"), Variable("y")),
    )
    assert eq[Variable("y")] == Equation(
        left=AlgebraObject(value=Variable("y")),
        right=AlgebraObject(Number("5/3"), Variable("x")),
    )


def test_solve_denominator(processor):
    assert Equation(
        left=processor.eval(AST("4u - 5/j")), right=processor.eval(AST("u/j - 20"))
    )[Variable("j")] == Equation(
        left=AlgebraObject(value=Variable("j")), right=AlgebraObject(Number("0.25"))
    )
    eq = Equation(left=processor.eval(AST("3/c + n/c")), right=processor.eval(AST("8")))
    assert eq[Variable("c")] == Equation(
        left=AlgebraObject(value=Variable("c")),
        right=AlgebraObject(
            value=Polynomial(
                [
                    AlgebraObject(Number("0.125"), Variable("n")),
                    AlgebraObject(Number("0.375")),
                ]
            )
        ),
    )
    assert eq[Variable("n")] == Equation(
        left=AlgebraObject(value=Variable("n")),
        right=AlgebraObject(
            value=Polynomial(
                [
                    AlgebraObject(Number(8), Variable("c")),
                    AlgebraObject(Number(-3)),
                ]
            )
        ),
    )


def test_solve_factorization(processor):
    eq = Equation(
        processor.eval(AST("n(2-3b) + 2 - 4b")), processor.eval(AST("2b - 2"))
    )
    assert eq[Variable("n")] == Equation(
        left=AlgebraObject(value=Variable("n")), right=AlgebraObject(Number(-2))
    )
    assert eq[Variable("b")] == Equation(
        left=AlgebraObject(value=Variable("b")), right=AlgebraObject(Number("2/3"))
    )

    eq = Equation(
        processor.eval(AST("1.5y(3x-6) + 3x - 5")), processor.eval(AST("x - 1"))
    )
    assert eq[Variable("y")] == Equation(
        left=AlgebraObject(value=Variable("y")), right=AlgebraObject(Number("-4/9"))
    )
    assert eq[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(2))
    )
    expected = processor.eval(AST("2√(S/(2hp + 2p))"))
    assert Equation(
        left=AlgebraObject(value=Variable("S")),
        right=processor.eval(AST("2pr^2 + 2pr^2h")),
    )[Variable("r")] == Equation(
        left=AlgebraObject(value=Variable("r")), right=Solutions({expected, -expected})
    )


def test_solve_formulas(processor):
    # a^2 + b^2 = c^2, b = 2√(c^2 - a^2) : b = sqrt(c^2 - a^2)
    # In this case, the engine assigns plus-minus sqrt(c^2 - a^2)
    right = AlgebraObject(
        value=Polynomial(
            [
                AlgebraObject(value=Variable("c"), exp=Number(2)),
                AlgebraObject(Number(-1), Variable("a"), exp=Number(2)),
            ]
        ),
        exp=Number("0.5"),
    )
    assert Equation(
        left=processor.eval(AST("a^2+b^2")),
        right=AlgebraObject(value=Variable("c"), exp=Number(2)),
    )[Variable("b")] == Equation(
        left=AlgebraObject(value=Variable("b")),
        right=Solutions((right, -right)),
    )
    # d = st, t = d/s
    assert Equation(
        left=AlgebraObject(value=Variable("d")), right=processor.eval(AST("st"))
    )[Variable("t")] == Equation(
        left=AlgebraObject(value=Variable("t")),
        right=AlgebraObject(
            value=Product(
                [
                    AlgebraObject(value=Variable("d")),
                    AlgebraObject(value=Variable("s"), exp=Number(-1)),
                ]
            ),
        ),
    )
    # C = Prt + P, P = C/(rt + 1)
    assert Equation(
        left=AlgebraObject(value=Variable("C")), right=processor.eval(AST("Prt + P"))
    )[Variable("P")] == Equation(
        left=AlgebraObject(value=Variable("P")),
        right=processor.eval(AST("C/(rt + 1)")),
    )
    # ax + b = c, b = c - ax
    assert Equation(
        left=processor.eval(AST("ax + b")), right=AlgebraObject(value=Variable("c"))
    )[Variable("b")] == Equation(
        left=AlgebraObject(value=Variable("b")), right=processor.eval(AST("c - ax"))
    )
    # y = mx + c, x = (y - c)/m
    assert Equation(
        left=AlgebraObject(value=Variable("y")), right=processor.eval(AST("mx + c"))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=processor.eval(AST("(y - c)/m")),
    )


def test_solve_quadratic(processor):
    assert Equation(
        left=processor.eval(AST("2x^2 + 3x - 5")), right=AlgebraObject(Number(0))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=Solutions(
            {
                AlgebraObject(Number(1)),
                AlgebraObject(Number("-2.5")),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("x^2 - 6x + 9")), right=AlgebraObject(Number(0))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")), right=AlgebraObject(Number(3))
    )
    assert Equation(
        left=processor.eval(AST("-3x^2 + 12x - 9")), right=AlgebraObject(Number(0))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=Solutions(
            {
                AlgebraObject(Number(1)),
                AlgebraObject(Number(3)),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("2x^2 + 13x")), right=AlgebraObject(Number(24))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=Solutions(
            {
                AlgebraObject(Number("1.5")),
                AlgebraObject(Number(-8)),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("x + 2√x")), right=AlgebraObject(Number(6))
    )[Variable("x")] == Equation(
        left=AlgebraObject(value=Variable("x")),
        right=Solutions(
            {
                AlgebraObject(Number(9)),
                AlgebraObject(Number(4)),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("(a-4)^2 ")),
        right=AlgebraObject(value=Variable("c"), exp=Number(2)),
    )[Variable("a")] == Equation(
        left=AlgebraObject(value=Variable("a")),
        right=Solutions(
            {
                processor.eval(AST("4 - c")),
                processor.eval(AST("4 + c")),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("ay^2 + by + c")), right=AlgebraObject(Number(0))
    )[Variable("y")] == Equation(
        left=AlgebraObject(value=Variable("y")),
        right=Solutions(
            {
                processor.eval(AST("(-b + (b^2 - 4ac)^0.5)/2a")),
                processor.eval(AST("(-b - (b^2 - 4ac)^0.5)/2a")),
            }
        ),
    )
    assert Equation(
        left=processor.eval(AST("-6ap^2 - 4ap + c")), right=AlgebraObject(Number(5))
    )[Variable("p")] == Equation(
        left=AlgebraObject(value=Variable("p")),
        right=Solutions(
            {
                processor.eval(AST("-1/3 - 2√(24ac + 16a^2 - 120a)/12a")),
                processor.eval(AST("-1/3 + 2√(24ac + 16a^2 - 120a)/12a")),
            }
        ),
    )


def test_solve_complex(processor):
    # Results would be too long to write out in object form
    inp1 = processor.eval(AST("p/x + q/(x+2) + r/(x-1)"))
    out1 = processor.eval(AST("5x - 7"))
    expected1 = Equation(
        left=processor.eval(
            AST("-5x^4 + rx^2 + qx^2 + px^2 + 2x^3 + 2rx - qx + px + 17x^2 - 14x")
        ),
        right=AlgebraObject(Number(2), Variable("p")),
    )
    assert Equation(left=inp1, right=out1)[Variable("x")] in {expected1, -expected1}
    expected = Equation(
        left=AlgebraObject(value=Variable("p")),
        right=processor.eval(
            AST("5x^2 - 7x - r - q + (-rx + 2qx - 2r - 2q)/(x^2 + x - 2)")
        ),
    )
    assert Equation(left=inp1, right=out1)[Variable("p")] == expected
    assert expected1[Variable("p")] == expected
