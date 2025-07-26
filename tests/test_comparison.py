from math import isclose

import pytest

from datatypes.nodes import *
from solving.comparison import Comparison, CompRel
from solving.solutions import IntervalUnion, SolutionSet
from solving.interval import INF, Interval
from solving.core import solve
from parsing import parser


x = Var("x")
y = Var("y")
z = Var("z")


def test_solve_basic():
    assert solve(Comparison(5 * x + 3, Const(13)), x) == Comparison(x, 2)
    assert solve(Comparison(2 * x - 3, Const(3)), x) == Comparison(x, 3)
    assert solve(Comparison(x / 4, Const(5)), x) == Comparison(x, 20)
    assert solve(Comparison(x + 6, 2 * x - 4), x) == Comparison(x, 10)


def test_solve_medium():
    assert solve(Comparison(3 * (x + 2), Const(15)), x) == Comparison(x, 3)
    assert solve(Comparison((2 * x + 1) / 3, Const(5)), x) == Comparison(x, 7)
    assert solve(Comparison((2 / x), Const(8)), x) == Comparison(x, Const(1, 4))
    assert solve(Comparison(4 * x - 3, 2 * (x + 5)), x) == Comparison(x, Const(13, 2))
    assert solve(Comparison(3 * x + 2 * y - 7, 5 * y + 4), x) == Comparison(
        x, y + Const(11, 3)
    )
    assert solve(
        Comparison((4 * x - 5) / 3 + 7 * x / 2, Const(11, 6)), x
    ) == Comparison(x, Const(21, 29))
    assert solve(Comparison(2 * x + 3 * y - z, Const(0)), x) == Comparison(
        x, Add(z / 2, -3 * y / 2)
    )
    assert solve(Comparison((x - 3) / (x + 2), Const(4)), x) == Comparison(
        x, Const(-11, 3)
    )
    assert solve(Comparison(3 * x**2, 9 + 2 * x**2), x) == Comparison(
        x, SolutionSet({3, -3}), CompRel.IN
    )

    eq = Comparison((3 / x) * y + 4, Const(9))
    assert solve(eq, x) == Comparison(x, 3 * y / 5)
    assert solve(eq, y) == Comparison(y, 5 * x / 3)


def test_solve_proportions():
    assert parser.eval("7/(x + 5) + x/(x + 4) = x/(x^2 + 9x + 20)") == Comparison(x, -7)
    assert parser.eval("5/(x + 7) + x/(x - 7) = 7/(x - 7)") == Comparison(x, -12)
    assert parser.eval("1 + 2/(x + 1) = (3x + 7)/(x^2 + 10x + 9)") == Comparison(
        x, SolutionSet({-4, -5}), CompRel.IN
    )
    u = Var("u")
    j = Var("j")
    n = Var("n")
    c = Var("c")

    assert solve(Comparison(4 * u - 5 / j, u / j - 20), j) == Comparison(j, Const(1, 4))
    eq = Comparison(3 / c + n / c, Const(8))
    assert solve(eq, c).expand() == Comparison(c, Add(n / 8, (Const(3, 8))))
    assert solve(eq, n) == Comparison(n, 8 * c - 3)


def test_solve_factorization():
    n = Var("n")
    b = Var("b")
    eq = Comparison(parser.eval("n(2-3b) + 2 - 4b"), 2 * b - 2)
    assert solve(eq, n) == Comparison(n, -2)
    assert solve(eq, b) == Comparison(b, Const(2, 3))

    eq = Comparison(3 * y / 2 * (3 * x - 6) + 3 * x - 5, x - 1)
    assert solve(eq, y) == Comparison(y, Const(-4, 9))
    assert solve(eq, x) == Comparison(x, 2)

    expected = parser.eval("(S/(2hp + 2p))^0.5")
    assert solve(
        Comparison(Var("S"), parser.eval("2pr^2 + 2pr^2h")), Var("r")
    ) == Comparison("r", SolutionSet({expected, -expected}), CompRel.IN)


def test_solve_formulas():
    # a^2 + b^2 = c^2, b = 2√(c^2 - a^2) : b = sqrt(c^2 - a^2)
    # In this case, the engine assigns plus-minus sqrt(c^2 - a^2)
    right = Add(Var("c") ** 2, -Var("a") ** 2) ** Const(1, 2)

    assert solve(
        Comparison(parser.eval("a^2+b^2"), Var("c") ** 2), Var("b")
    ) == Comparison("b", SolutionSet({right, -right}), CompRel.IN)
    # d = st, t = d/s
    assert solve(Comparison(Var("d"), Var("s") * Var("t")), Var("t")) == Comparison(
        "t", Var("d") / Var("s")
    )

    # C = Prt + P, P = C/(rt + 1)
    assert Comparison(Var("C"), parser.eval("Prt + P")).solve_for(
        Var("P")
    ) == Comparison(
        "P",
        parser.eval("C/(rt + 1)"),
    )
    # ax + b = c, b = c - ax
    assert Comparison(parser.eval("ax + b"), Var("c")).solve_for(
        Var("b")
    ) == Comparison(Var("b"), parser.eval("c - ax"))
    # y = mx + c, x = (y - c)/m
    assert Comparison(y, parser.eval("mx + c")).solve_for(x) == Comparison(
        x, parser.eval("(y - c)/m")
    )


def test_solve_quadratic():

    assert parser.eval("2x^2 + 3x - 5 = 0") == Comparison(
        x, SolutionSet({1, Const(-5, 2)}), CompRel.IN
    )
    assert parser.eval("x^2 - 6x + 9 = 0") == Comparison(x, 3)
    assert parser.eval("-3x^2 + 12x - 9 = 0") == Comparison(
        x, SolutionSet({1, 3}), CompRel.IN
    )
    assert parser.eval("2x^2 + 13x = 24") == Comparison(
        x, SolutionSet({-8, Const(3, 2)}), CompRel.IN
    )
    assert parser.eval("1/(x-5)^0.5 + x/(x-5)^0.5 = 7") == Comparison(
        x, SolutionSet({41, 6}), CompRel.IN
    )

    assert solve(
        Comparison(parser.eval("(a-4)^2 "), Var("c") ** 2), Var("a")
    ) == Comparison("a", SolutionSet({4 - Var("c"), 4 + Var("c")}), CompRel.IN)
    assert solve(Comparison(parser.eval("ay^2 + by + c"), Const(0)), y) == Comparison(
        y,
        SolutionSet(
            {
                parser.eval("(-b + (b^2 - 4ac)^0.5)/2a"),
                parser.eval("(-b - (b^2 - 4ac)^0.5)/2a"),
            }
        ),
        CompRel.IN,
    )


def test_solve_inequalities():
    assert solve(Comparison(2 * x + 3, Const(13), CompRel.GT), x).right == Interval(
        5, None, (True, True)
    )
    assert solve(Comparison(3 * x + 2, 5 * x - 4, CompRel.LT), x).right == Interval(
        3, None, (True, True)
    )
    assert solve(
        Comparison((x + 1) / (x - 1), Const(2), CompRel.GE), x
    ).right == Interval(1, 3, (True, False))
    assert solve(
        Comparison(x - 5 * x**0.5 / 2, Const(-1), CompRel.GT), x
    ).right == IntervalUnion(
        [Interval(0, Const(1, 4), (False, True)), Interval(4, None, (True, True))]
    )
    assert solve(
        Comparison((x + 1) * x**2 / (x - 1), Const(0), CompRel.LE), x
    ).right == Interval(-1, 1, (False, True))
    assert solve(
        Comparison((x + 1) * x**2 / (x - 1), Const(0), CompRel.LE), x
    ).right == Interval(-1, 1, (False, True))
    assert solve(
        Comparison((x + 2) * x**0.5 / (x - 1), Const(0), CompRel.GE), x
    ).right == ({0}, Interval(1, None, (True, True)))


def test_solve_radicals():
    # 3x^3=(2+((x-3)^3)^(1/5)+x^.5)^(1/3)-x^2
    # (a+3)^.5+(a^2-4)^(1/3)=4
    # (a^2+3a+2)^.25+(a+1)^(1/3)=3
    assert parser.eval("x + √(2x - 1) + √(2x + 3) = 2.5").right == Const(1, 2)
    # approximations
    assert isclose(
        parser.eval("x + √(x - 1) + √(2x + 3) = 9").right, 3.9694, abs_tol=1e-4
    )
    assert isclose(parser.eval("(a+(a+a^.5)^.5)^.5=2").right, 2.1119, abs_tol=1e-4)
    assert isclose(
        parser.eval("(1+(2+(3+a)^.5)^.5)^.5+(a-1)^(1/3)=3").right, 2.8977, abs_tol=1e-4
    )
    # rhs = sorted(parser.eval("(1+((3+a)^.5-2)^.5)^.5+(a-1)^(1/3)/a=1.7").right)
    # assert all(
    #     starmap(
    #         lambda a, b: isclose(a, b, abs_tol=1e-4), zip(rhs, [1.5788, 4.8105, 6.5235])
    #     )
    # )


def test_solve_edge():
    # Extraneous solutions
    assert parser.eval("2x - x^0.5 = 6").right == 4
    # Requiring numeric approximation verification
    assert parser.eval("(2x+3)^0.5+(x-1)^0.5=4").right == 44 - 24 * Const(3) ** 0.5

    # Infinite Solutions
    assert parser.eval("x => 0x = 0").right == INF
    assert parser.eval("(x-2)^2 = (x^2 - 4x + 4)").right == INF
    # No solution
    assert not parser.eval("x + 2 = x - 4").right
    assert not parser.eval("x > x").right
    assert not parser.eval("y => mx > -mx").right


@pytest.mark.skip(reason="irrelevant")
def test_solve_complex():
    # Results would be too long to write out in object form
    eq = Comparison(
        parser.eval("-5x^4 + rx^2 + qx^2 + px^2 + 2x^3 + 2rx - qx + px + 17x^2 - 14x"),
        (Const(2), Var("p")),
    )
    expected = Comparison(
        (Var("p")),
        parser.eval("5x^2 - 7x - r - q + (-rx + 2qx - 2r - 2q)/(x^2 + x - 2)"),
    )
    assert (
        Comparison(
            parser.eval("p/x + q/(x+2) + r/(x-1)"),
            parser.eval("5x - 7"),
        ).solve_for(Var("p"))
        == expected
    )
    assert eq.solve_for(Var("p")) == expected
