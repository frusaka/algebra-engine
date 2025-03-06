from datatypes import *


v = Variable("v")
w = Variable("w")
x = Variable("x")
y = Variable("y")
z = Variable("z")


def test_solve_linear(processor):
    # Basic system of two equations
    assert processor.eval("(x, y) -> x + y = 5; 3x = 4y + 1") == Comparison(
        (x, y), (Term(Number(3)), Term(Number(2)))
    )
    processor.eval("(x, y) -> 2x + 3y = 7; x - y = 2") == Comparison(
        (x, y), (Term(Number(13, 5)), Term(Number(3, 5)))
    )
    processor.eval("(x, y) -> 2x - 3 = 5y + 7; 2x + 2y = 14") == Comparison(
        (x, y), (Term(Number(15, 4)), Term(Number(-1, 2)))
    )

    # System of 3 equations
    assert (
        processor.eval(
            """
            (x, y, z) ->
            2x - y + 3z = 5;
            x + 4y - 2z = 6;
            3x + 2y + z = 8
            """
        )
        == Comparison(
            (x, y, z), (Term(Number(-2, 7)), Term(Number(3)), Term(Number(20, 7)))
        )
    )
    assert (
        processor.eval(
            """
            (x, y, z) ->
            x + 2y - z = 4;
            3x - y + 4z = 10;
            2x + 3y + z = 7
            """
        )
        == Comparison(
            (x, y, z),
            (Term(Number(53, 14)), Term(Number(-1, 14)), Term(Number(-5, 14))),
        )
    )
    # Advanced: System of 5 equations
    assert (
        processor.eval(
            """
            (v, w, x, y, z) ->
            x + 2y - z + w + 3v = 10;
            2x - y + 3z - 2w + v = -5;
            3x + 4y + 2z + w - v = 12;
            x - 3y + 4z + 2w + 5v = 7;
            -2x + y - 3z + w + 4v = -8
            """
        )
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


def test_solve_quadratic_linear(processor):
    assert processor.eval("(v, w) -> v + w = 10; vw = 21") == Comparison(
        (v, w),
        Collection(
            {
                (Term(Number(3)), Term(Number(7))),
                (Term(Number(7)), Term(Number(3))),
            }
        ),
    )
    assert processor.eval("(x, y) -> y = x^2 - 3x - 46; y = -3x + 3") == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(-7)), Term(Number(24))),
                (Term(Number(7)), Term(Number(-18))),
            }
        ),
    )
    assert processor.eval("(x, y) -> y = x^2 - 19x + 58; y = -3x - 5") == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(9)), Term(Number(-32))),
                (Term(Number(7)), Term(Number(-26))),
            }
        ),
    )
    assert processor.eval("(x, y) -> (x - 2)^2 + y^2 = 58; x + y = -2") == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(5)), Term(Number(-7))),
                (Term(Number(-5)), Term(Number(3))),
            }
        ),
    )
    assert processor.eval("(x, y) -> (x + 3)^2 + y^2 = 25; 2x + y = 4") == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(2)), Term(Number(0))),
                (Term(Number(0)), Term(Number(4))),
            }
        ),
    )
    assert processor.eval(
        "(x, y, z) -> xy = z; x + y = -7; x + z = -3y - 1"
    ) == Comparison(
        (x, y, z),
        Collection(
            {
                (Term(Number(-4)), Term(Number(-3)), Term(Number(12))),
                (Term(Number(-5)), Term(Number(-2)), Term(Number(10))),
            }
        ),
    )


def test_solve_2_quadratic(processor):
    assert processor.eval("(x, y) -> x^2 + y^2 = 9; x^2 + 2y^2 = 9") == Comparison(
        (x, y),
        Collection(
            {
                (Term(Number(3)), Term(Number(0))),
                (Term(Number(-3)), Term(Number(0))),
            }
        ),
    )
    assert processor.eval("(x, y) -> x^2 + y^2 = 25; x^2 - 9 = y^2 - 2") == Comparison(
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

    assert processor.eval("(x, y) -> x^2 + 11 = 4y^2; (x^2 + y) = 28") == Comparison(
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
