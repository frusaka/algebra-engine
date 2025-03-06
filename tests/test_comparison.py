from typing import Any
from datatypes import *


def test_solve_basic(processor):
    assert Comparison(processor.eval("5x+3"), Term(Number(13)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(2)))

    assert Comparison(processor.eval("2x-7"), Term(Number(3)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(5)))

    assert Comparison(processor.eval("x/4"), Term(Number(5)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(20)))

    assert Comparison(processor.eval("x+6"), processor.eval("2x-4"))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(10)))


def test_solve_medium(processor):
    assert Comparison(processor.eval("3(x+2)"), Term(Number(15)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(3)))

    assert Comparison(processor.eval("(2x+1)/3"), Term(Number(5)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(7)))

    assert Comparison(processor.eval("2/x"), Term(Number(8)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(1, 4)))

    assert Comparison(processor.eval("4x-3"), right=processor.eval("2(x+5)"))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(13, 2)))

    assert Comparison(processor.eval("3x+2y-7"), processor.eval("5y+4"))[
        Variable("x")
    ] == Comparison(
        left=Term(value=Variable("x")),
        right=Term(
            value=Polynomial(
                [
                    Term(value=Variable("y")),
                    Term(Number(11, 3)),
                ]
            )
        ),
    )
    assert Comparison(
        left=processor.eval("(4x-5)/3 + 7x/2"),
        right=Term(Number(11, 6)),
    )[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(21, 29))
    )

    assert Comparison(left=processor.eval("2x+3y-z"), right=Term(Number(0)))[
        Variable("x")
    ] == Comparison(
        left=Term(value=Variable("x")),
        right=Term(
            value=Polynomial(
                [
                    Term(Number(1, 2), Variable("z")),
                    Term(Number(-3, 2), Variable("y")),
                ]
            )
        ),
    )

    assert Comparison(left=processor.eval("(x-3)/(x+2)"), right=Term(Number(4)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(-11, 3)))

    assert Comparison(processor.eval("3x^2"), processor.eval("9 + 2x^2"))[
        Variable("x")
    ] == System(
        {
            Comparison(Term(value=Variable("x")), Term(Number(3))),
            Comparison(Term(value=Variable("x")), Term(Number(-3))),
        }
    )
    eq = Comparison(left=processor.eval("(3/x)y + 4"), right=Term(Number(9)))
    assert eq[Variable("x")] == Comparison(
        left=Term(value=Variable("x")),
        right=Term(Number(3, 5), Variable("y")),
    )
    assert eq[Variable("y")] == Comparison(
        left=Term(value=Variable("y")),
        right=Term(Number(5, 3), Variable("x")),
    )


def test_solve_denominator(processor):
    assert Comparison(
        left=processor.eval("4u - 5/j"), right=processor.eval("u/j - 20")
    )[Variable("j")] == Comparison(
        left=Term(value=Variable("j")), right=Term(Number(1, 4))
    )
    eq = Comparison(left=processor.eval("3/c + n/c"), right=Term(Number(8)))
    assert eq[Variable("c")] == Comparison(
        left=Term(value=Variable("c")),
        right=Term(
            value=Polynomial(
                [
                    Term(Number(1, 8), Variable("n")),
                    Term(Number(3, 8)),
                ]
            )
        ),
    )
    assert eq[Variable("n")] == Comparison(
        left=Term(value=Variable("n")),
        right=Term(
            value=Polynomial(
                [
                    Term(Number(8), Variable("c")),
                    Term(Number(-3)),
                ]
            )
        ),
    )


def test_solve_proportions(processor):
    assert processor.eval("7/(x + 5) + x/(x + 4) = x/(x^2 + 9x + 20)")[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(-7)))
    assert processor.eval("5/(x + 7) + x/(x - 7) = 7/(x - 7)")[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(-12)))
    assert processor.eval("1 + 2/(x + 1) = (3x + 7)/(x^2 + 10x + 9)")[
        Variable("x")
    ] == System(
        {
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-4))),
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-5))),
        }
    )


def test_solve_factorization(processor):
    eq = Comparison(processor.eval("n(2-3b) + 2 - 4b"), processor.eval("2b - 2"))
    assert eq[Variable("n")] == Comparison(
        left=Term(value=Variable("n")), right=Term(Number(-2))
    )
    assert eq[Variable("b")] == Comparison(
        left=Term(value=Variable("b")), right=Term(Number(2, 3))
    )

    eq = Comparison(processor.eval("1.5y(3x-6) + 3x - 5"), processor.eval("x - 1"))
    assert eq[Variable("y")] == Comparison(
        left=Term(value=Variable("y")), right=Term(Number(-4, 9))
    )
    assert eq[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(2))
    )
    expected = processor.eval("2√(S/(2hp + 2p))")
    assert Comparison(
        left=Term(value=Variable("S")),
        right=processor.eval("2pr^2 + 2pr^2h"),
    )[Variable("r")] == System(
        {
            Comparison(left=Term(value=Variable("r")), right=expected),
            Comparison(left=Term(value=Variable("r")), right=-expected),
        }
    )


def test_solve_formulas(processor):
    # a^2 + b^2 = c^2, b = 2√(c^2 - a^2) : b = sqrt(c^2 - a^2)
    # In this case, the engine assigns plus-minus sqrt(c^2 - a^2)
    right = Term(
        value=Polynomial(
            [
                Term(value=Variable("c"), exp=Number(2)),
                Term(Number(-1), Variable("a"), exp=Number(2)),
            ]
        ),
        exp=Number(1, 2),
    )
    assert Comparison(
        left=processor.eval("a^2+b^2"),
        right=Term(value=Variable("c"), exp=Number(2)),
    )[Variable("b")] == System(
        {
            Comparison(
                left=Term(value=Variable("b")),
                right=right,
            ),
            Comparison(
                left=Term(value=Variable("b")),
                right=-right,
            ),
        }
    )
    # d = st, t = d/s
    assert Comparison(left=Term(value=Variable("d")), right=processor.eval("st"))[
        Variable("t")
    ] == Comparison(
        left=Term(value=Variable("t")),
        right=Term(
            value=Product(
                [
                    Term(value=Variable("d")),
                    Term(value=Variable("s"), exp=Number(-1)),
                ]
            ),
        ),
    )
    # C = Prt + P, P = C/(rt + 1)
    assert Comparison(left=Term(value=Variable("C")), right=processor.eval("Prt + P"))[
        Variable("P")
    ] == Comparison(
        left=Term(value=Variable("P")),
        right=processor.eval("C/(rt + 1)"),
    )
    # ax + b = c, b = c - ax
    assert Comparison(left=processor.eval("ax + b"), right=Term(value=Variable("c")))[
        Variable("b")
    ] == Comparison(left=Term(value=Variable("b")), right=processor.eval("c - ax"))
    # y = mx + c, x = (y - c)/m
    assert Comparison(left=Term(value=Variable("y")), right=processor.eval("mx + c"))[
        Variable("x")
    ] == Comparison(
        left=Term(value=Variable("x")),
        right=processor.eval("(y - c)/m"),
    )


def test_solve_quadratic(processor):
    assert Comparison(left=processor.eval("2x^2 + 3x - 5"), right=Term(Number(0)))[
        Variable("x")
    ] == System(
        {
            Comparison(left=Term(value=Variable("x")), right=Term(Number(1))),
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-5, 2))),
        }
    )
    assert Comparison(left=processor.eval("x^2 - 6x + 9"), right=Term(Number(0)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(3)))
    assert Comparison(left=processor.eval("-3x^2 + 12x - 9"), right=Term(Number(0)))[
        Variable("x")
    ] == System(
        {
            Comparison(left=Term(value=Variable("x")), right=Term(Number(1))),
            Comparison(left=Term(value=Variable("x")), right=Term(Number(3))),
        }
    )
    assert Comparison(left=processor.eval("2x^2 + 13x"), right=Term(Number(24)))[
        Variable("x")
    ] == System(
        {
            Comparison(left=Term(value=Variable("x")), right=Term(Number(3, 2))),
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-8))),
        }
    )
    assert Comparison(
        left=processor.eval("(a-4)^2 "),
        right=Term(value=Variable("c"), exp=Number(2)),
    )[Variable("a")] == System(
        {
            Comparison(left=Term(value=Variable("a")), right=processor.eval("4 - c")),
            Comparison(left=Term(value=Variable("a")), right=processor.eval("4 + c")),
        }
    )
    assert Comparison(left=processor.eval("ay^2 + by + c"), right=Term(Number(0)))[
        Variable("y")
    ] == System(
        {
            Comparison(
                left=Term(value=Variable("y")),
                right=processor.eval("(-b + (b^2 - 4ac)^0.5)/2a"),
            ),
            Comparison(
                left=Term(value=Variable("y")),
                right=processor.eval("(-b - (b^2 - 4ac)^0.5)/2a"),
            ),
        }
    )
    assert Comparison(left=processor.eval("-6ap^2 - 4ap + c"), right=Term(Number(5)))[
        Variable("p")
    ] == System(
        {
            Comparison(
                left=Term(value=Variable("p")),
                right=processor.eval("-1/3 - 2√(24ac + 16a^2 - 120a)/12a"),
            ),
            Comparison(
                left=Term(value=Variable("p")),
                right=processor.eval("-1/3 + 2√(24ac + 16a^2 - 120a)/12a"),
            ),
        }
    )


def test_solve_edge(processor):
    # Extraneous solutions
    assert processor.eval("x -> 2x - 2√x = 6").right == Term(Number(4))
    # Infinite Solutions
    assert processor.eval("x -> 0x = 0").right == Collection({"ℂ"})
    assert processor.eval("x -> x + 4 = x + 4").right == Collection({"ℂ"})
    assert processor.eval("x -> x - 2 > x - 4").right == Collection({"ℝ"})
    # No Solutions
    assert not processor.eval("x -> x + 2 = x - 4").right
    assert not processor.eval("x -> x > x").right


def test_solve_complex(processor):
    # Results would be too long to write out in object form
    eq = Comparison(
        left=processor.eval(
            "-5x^4 + rx^2 + qx^2 + px^2 + 2x^3 + 2rx - qx + px + 17x^2 - 14x"
        ),
        right=Term(Number(2), Variable("p")),
    )
    expected = Comparison(
        left=Term(value=Variable("p")),
        right=processor.eval("5x^2 - 7x - r - q + (-rx + 2qx - 2r - 2q)/(x^2 + x - 2)"),
    )
    assert (
        Comparison(
            left=processor.eval("p/x + q/(x+2) + r/(x-1)"),
            right=processor.eval("5x - 7"),
        )[Variable("p")]
        == expected
    )
    assert eq[Variable("p")] == expected
