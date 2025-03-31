from datatypes import *
from processing import AST


def test_solve_basic():
    assert Comparison(AST("5x+3").eval(), Term(Number(13)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(2)))

    assert Comparison(AST("2x-7").eval(), Term(Number(3)))[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(5))
    )

    assert Comparison(AST("x/4").eval(), Term(Number(5)))[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(20))
    )

    assert Comparison(AST("x+6").eval(), AST("2x-4").eval())[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(10)))


def test_solve_medium():
    assert Comparison(AST("3(x+2)").eval(), Term(Number(15)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(3)))

    assert Comparison(AST("(2x+1)/3").eval(), Term(Number(5)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(7)))

    assert Comparison(AST("2/x").eval(), Term(Number(8)))[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(1, 4))
    )

    assert Comparison(AST("4x-3").eval(), right=AST("2(x+5)").eval())[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(13, 2)))

    assert Comparison(AST("3x+2y-7").eval(), AST("5y+4").eval())[
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
        left=AST("(4x-5)/3 + 7x/2").eval(),
        right=Term(Number(11, 6)),
    )[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(21, 29)))

    assert Comparison(left=AST("2x+3y-z").eval(), right=Term(Number(0)))[
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

    assert Comparison(left=AST("(x-3)/(x+2)").eval(), right=Term(Number(4)))[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(-11, 3)))

    assert Comparison(AST("3x^2").eval(), AST("9 + 2x^2").eval())[
        Variable("x")
    ] == System(
        {
            Comparison(Term(value=Variable("x")), Term(Number(3))),
            Comparison(Term(value=Variable("x")), Term(Number(-3))),
        }
    )
    eq = Comparison(left=AST("(3/x)y + 4").eval(), right=Term(Number(9)))
    assert eq[Variable("x")] == Comparison(
        left=Term(value=Variable("x")),
        right=Term(Number(3, 5), Variable("y")),
    )
    assert eq[Variable("y")] == Comparison(
        left=Term(value=Variable("y")),
        right=Term(Number(5, 3), Variable("x")),
    )


def test_solve_denominator():
    assert Comparison(left=AST("4u - 5/j").eval(), right=AST("u/j - 20").eval())[
        Variable("j")
    ] == Comparison(left=Term(value=Variable("j")), right=Term(Number(1, 4)))
    eq = Comparison(left=AST("3/c + n/c").eval(), right=Term(Number(8)))
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


def test_solve_proportions():
    assert AST("7/(x + 5) + x/(x + 4) = x/(x^2 + 9x + 20)").eval()[
        Variable("x")
    ] == Comparison(left=Term(value=Variable("x")), right=Term(Number(-7)))
    assert AST("5/(x + 7) + x/(x - 7) = 7/(x - 7)").eval()[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(-12))
    )
    assert AST("1 + 2/(x + 1) = (3x + 7)/(x^2 + 10x + 9)").eval()[
        Variable("x")
    ] == System(
        {
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-4))),
            Comparison(left=Term(value=Variable("x")), right=Term(Number(-5))),
        }
    )


def test_solve_factorization():
    eq = Comparison(AST("n(2-3b) + 2 - 4b").eval(), AST("2b - 2").eval())
    assert eq[Variable("n")] == Comparison(
        left=Term(value=Variable("n")), right=Term(Number(-2))
    )
    assert eq[Variable("b")] == Comparison(
        left=Term(value=Variable("b")), right=Term(Number(2, 3))
    )

    eq = Comparison(AST("1.5y(3x-6) + 3x - 5").eval(), AST("x - 1").eval())
    assert eq[Variable("y")] == Comparison(
        left=Term(value=Variable("y")), right=Term(Number(-4, 9))
    )
    assert eq[Variable("x")] == Comparison(
        left=Term(value=Variable("x")), right=Term(Number(2))
    )
    expected = AST("2√(S/(2hp + 2p))").eval()
    assert Comparison(
        left=Term(value=Variable("S")),
        right=AST("2pr^2 + 2pr^2h").eval(),
    )[Variable("r")] == System(
        {
            Comparison(left=Term(value=Variable("r")), right=expected),
            Comparison(left=Term(value=Variable("r")), right=-expected),
        }
    )


def test_solve_formulas():
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
        left=AST("a^2+b^2").eval(),
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
    assert Comparison(left=Term(value=Variable("d")), right=AST("st").eval())[
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
    assert Comparison(left=Term(value=Variable("C")), right=AST("Prt + P").eval())[
        Variable("P")
    ] == Comparison(
        left=Term(value=Variable("P")),
        right=AST("C/(rt + 1)").eval(),
    )
    # ax + b = c, b = c - ax
    assert Comparison(left=AST("ax + b").eval(), right=Term(value=Variable("c")))[
        Variable("b")
    ] == Comparison(left=Term(value=Variable("b")), right=AST("c - ax").eval())
    # y = mx + c, x = (y - c)/m
    assert Comparison(left=Term(value=Variable("y")), right=AST("mx + c").eval())[
        Variable("x")
    ] == Comparison(
        left=Term(value=Variable("x")),
        right=AST("(y - c)/m").eval(),
    )


def test_solve_quadratic():

    assert AST("x -> 2x^2 + 3x - 5 = 0").eval() == Comparison(
        left=Variable("x"), right=Collection({Term(Number(1)), Term(Number(-5, 2))})
    )
    assert AST("x -> x^2 - 6x + 9 = 0").eval() == Comparison(
        left=Variable("x"), right=Term(Number(3))
    )
    assert AST("x -> -3x^2 + 12x - 9 = 0").eval() == Comparison(
        left=Variable("x"), right=Collection({Term(Number(1)), Term(Number(3))})
    )
    assert AST("x -> 2x^2 + 13x = 24").eval() == Comparison(
        left=Variable("x"), right=Collection({Term(Number(3, 2)), Term(Number(-8))})
    )
    assert AST("x -> 1/(x-5)^0.5 + x/(x-5)^0.5 = 7").eval() == Comparison(
        Variable("x"), Collection({Term(Number(6)), Term(Number(41))})
    )

    assert Comparison(
        left=AST("(a-4)^2 ").eval(),
        right=Term(value=Variable("c"), exp=Number(2)),
    )[Variable("a")] == System(
        {
            Comparison(left=Term(value=Variable("a")), right=AST("4 - c").eval()),
            Comparison(left=Term(value=Variable("a")), right=AST("4 + c").eval()),
        }
    )
    assert Comparison(left=AST("ay^2 + by + c").eval(), right=Term(Number(0)))[
        Variable("y")
    ] == System(
        {
            Comparison(
                left=Term(value=Variable("y")),
                right=AST("(-b + (b^2 - 4ac)^0.5)/2a").eval(),
            ),
            Comparison(
                left=Term(value=Variable("y")),
                right=AST("(-b - (b^2 - 4ac)^0.5)/2a").eval(),
            ),
        }
    )


def test_solve_edge():
    # Extraneous solutions
    assert AST("x -> 2x - 2√x = 6").eval().right == Term(Number(4))
    # Infinite Solutions
    assert AST("x -> 0x = 0").eval().right == Collection({"ℂ"})
    assert AST("x -> x + 4 = x + 4").eval().right == Collection({"ℂ"})
    assert AST("x -> x - 2 > x - 4").eval().right == Collection({"ℝ"})
    # No Solutions
    assert not AST("x -> x + 2 = x - 4").eval().right
    assert not AST("x -> x > x").eval().right


def test_solve_complex():
    # Results would be too long to write out in object form
    eq = Comparison(
        left=AST(
            "-5x^4 + rx^2 + qx^2 + px^2 + 2x^3 + 2rx - qx + px + 17x^2 - 14x"
        ).eval(),
        right=Term(Number(2), Variable("p")),
    )
    expected = Comparison(
        left=Term(value=Variable("p")),
        right=AST("5x^2 - 7x - r - q + (-rx + 2qx - 2r - 2q)/(x^2 + x - 2)").eval(),
    )
    assert (
        Comparison(
            left=AST("p/x + q/(x+2) + r/(x-1)").eval(),
            right=AST("5x - 7").eval(),
        )[Variable("p")]
        == expected
    )
    assert eq[Variable("p")] == expected
