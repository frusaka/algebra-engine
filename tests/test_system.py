from datatypes import *
from processing import AST

v = Variable("v")
w = Variable("w")
x = Variable("x")
y = Variable("y")
z = Variable("z")


def test_solve_linear():
    # Basic system of two equations
    assert AST("(x, y) -> x + y = 5; 3x = 4y + 1").eval() == Comparison(
        (x, y), (Term(Number(3)), Term(Number(2)))
    )
    AST("(x, y) -> 2x + 3y = 7; x - y = 2").eval() == Comparison(
        (x, y), (Term(Number(13, 5)), Term(Number(3, 5)))
    )
    AST("(x, y) -> 2x - 3 = 5y + 7; 2x + 2y = 14").eval() == Comparison(
        (x, y), (Term(Number(15, 4)), Term(Number(-1, 2)))
    )

    # System of 3 equations
    assert (
        AST(
            """
            (x, y, z) ->
            2x - y + 3z = 5;
            x + 4y - 2z = 6;
            3x + 2y + z = 8
            """
        ).eval()
        == Comparison(
            (x, y, z), (Term(Number(-2, 7)), Term(Number(3)), Term(Number(20, 7)))
        )
    )
    assert (
        AST(
            """
            (x, y, z) ->
            x + 2y - z = 4;
            3x - y + 4z = 10;
            2x + 3y + z = 7
            """
        ).eval()
        == Comparison(
            (x, y, z),
            (Term(Number(53, 14)), Term(Number(-1, 14)), Term(Number(-5, 14))),
        )
    )
    # Advanced: System of 5 equations
    assert (
        AST(
            """
            (v, w, x, y, z) ->
            x + 2y - z + w + 3v = 10;
            2x - y + 3z - 2w + v = -5;
            3x + 4y + 2z + w - v = 12;
            x - 3y + 4z + 2w + 5v = 7;
            -2x + y - 3z + w + 4v = -8
            """
        ).eval()
        == Comparison(
            (v, w, x, y, z),
            (
                Term(Number(-43, 32)),
                Term(Number(201, 32)),
                Term(Number(421, 40)),
                Term(Number(-131, 32)),
                Term(Number(-433, 80)),
            ),
        )
    )


def test_solve_quadratic_linear():
    assert AST("(v, w) -> v + w = 10; vw = 21").eval() == Comparison(
        (v, w),
        Collection(
            {
                (Term(Number(3)), Term(Number(7))),
                (Term(Number(7)), Term(Number(3))),
            }
        ),
    )
    assert AST("(x, y) -> y = x^2 - 3x - 46; y = -3x + 3").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(-7)), Term(Number(24))),
                (Term(Number(7)), Term(Number(-18))),
            }
        ),
    )
    assert AST("(x, y) -> y = x^2 - 19x + 58; y = -3x - 5").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(9)), Term(Number(-32))),
                (Term(Number(7)), Term(Number(-26))),
            }
        ),
    )
    assert AST("(x, y) -> (x - 2)^2 + y^2 = 58; x + y = -2").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(5)), Term(Number(-7))),
                (Term(Number(-5)), Term(Number(3))),
            }
        ),
    )
    assert AST("(x, y) -> (x + 3)^2 + y^2 = 25; 2x + y = 4").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(2)), Term(Number(0))),
                (Term(Number(0)), Term(Number(4))),
            }
        ),
    )
    assert AST("(x, y, z) -> xy = z; x + y = -7; x + z = -3y - 1").eval() == Comparison(
        (x, y, z),
        Collection(
            {
                (Term(Number(-4)), Term(Number(-3)), Term(Number(12))),
                (Term(Number(-5)), Term(Number(-2)), Term(Number(10))),
            }
        ),
    )


def test_solve_2_quadratic():
    assert AST("(x, y) -> x^2 + y^2 = 9; x^2 + 2y^2 = 9").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(3)), Term(Number(0))),
                (Term(Number(-3)), Term(Number(0))),
            }
        ),
    )
    assert AST("(x, y) -> x^2 + y^2 = 25; x^2 - 9 = y^2 - 2").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(-4)), Term(Number(-3))),
                (Term(Number(-4)), Term(Number(3))),
                (Term(Number(4)), Term(Number(-3))),
                (Term(Number(4)), Term(Number(3))),
            }
        ),
    )

    assert AST("(x, y) -> x^2 + 11 = 4y^2; (x^2 + y) = 28").eval() == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(5)), Term(Number(3))),
                (Term(Number(-5)), Term(Number(3))),
                (Term(Number(5, 2), Number(5), Number(1, 2)), Term(Number(-13, 4))),
                (Term(Number(-5, 2), Number(5), Number(1, 2)), Term(Number(-13, 4))),
            }
        ),
    )
