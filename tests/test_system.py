from data_types import *


v = Term(value=Variable("v"))
w = Term(value=Variable("w"))
x = Term(value=Variable("x"))
y = Term(value=Variable("y"))
z = Term(value=Variable("z"))


def test_solve_linear(processor, AST):
    # Basic system of two equations
    assert processor.eval(AST("(x, y) -> x + y = 5; 3x = 4y + 1")) == System(
        {Comparison(x, Term(Number(3))), Comparison(y, Term(Number(2)))}
    )
    processor.eval(AST("(x, y) -> 2x + 3y = 7; x - y = 2")) == System(
        {Comparison(x, Term(Number(13, 5))), Comparison(y, Term(Number(3, 5)))}
    )
    processor.eval(AST("(x, y) -> 2x - 3 = 5y + 7; 2x + 2y = 14")) == System(
        {Comparison(x, Term(Number(15, 4))), Comparison(y, Term(Number(-1, 2)))}
    )

    # System of 3 equations
    assert (
        processor.eval(
            AST(
                """
            (x, y, z) ->
            2x - y + 3z = 5;
            x + 4y - 2z = 6;
            3x + 2y + z = 8
            """
            )
        )
        == System(
            {
                Comparison(x, Term(Number(-2, 7))),
                Comparison(y, Term(Number(3))),
                Comparison(z, Term(Number(20, 7))),
            }
        )
    )
    assert (
        processor.eval(
            AST(
                """
            (x, y, z) ->
            x + 2y - z = 4;
            3x - y + 4z = 10;
            2x + 3y + z = 7
            """
            )
        )
        == System(
            {
                Comparison(x, Term(Number(53, 14))),
                Comparison(y, Term(Number(-1, 14))),
                Comparison(z, Term(Number(-5, 14))),
            }
        )
    )
    # Advanced: System of 5 equations
    assert (
        processor.eval(
            AST(
                """
            (v, w, x, y, z) ->
            x + 2y - z + w + 3v = 10;
            2x - y + 3z - 2w + v = -5;
            3x + 4y + 2z + w - v = 12;
            x - 3y + 4z + 2w + 5v = 7;
            -2x + y - 3z + w + 4v = -8
            """
            )
        )
        == System(
            {
                Comparison(v, Term(Number(-43, 32))),
                Comparison(w, Term(Number(201, 32))),
                Comparison(x, Term(Number(421, 40))),
                Comparison(y, Term(Number(-131, 32))),
                Comparison(z, Term(Number(-433, 80))),
            }
        )
    )


def test_solve_quadratic_linear(processor, AST):
    assert processor.eval(AST("(v, w) -> v + w = 10; vw = 21")) == System(
        {
            System({Comparison(v, Term(Number(3))), Comparison(w, Term(Number(7)))}),
            System({Comparison(v, Term(Number(7))), Comparison(w, Term(Number(3)))}),
        }
    )
    assert processor.eval(AST("(x, y) -> y = x^2 - 3x - 46; y = -3x + 3")) == System(
        {
            System({Comparison(x, Term(Number(-7))), Comparison(y, Term(Number(24)))}),
            System({Comparison(x, Term(Number(7))), Comparison(y, Term(Number(-18)))}),
        }
    )
    assert processor.eval(AST("(x, y) -> y = x^2 - 19x + 58; y = -3x - 5")) == System(
        {
            System({Comparison(x, Term(Number(9))), Comparison(y, Term(Number(-32)))}),
            System({Comparison(x, Term(Number(7))), Comparison(y, Term(Number(-26)))}),
        }
    )
    assert processor.eval(AST("(x, y) -> (x - 2)^2 + y^2 = 58; x + y = -2")) == System(
        {
            System({Comparison(x, Term(Number(5))), Comparison(y, Term(Number(-7)))}),
            System({Comparison(x, Term(Number(-5))), Comparison(y, Term(Number(3)))}),
        }
    )
    assert processor.eval(AST("(x, y) -> (x + 3)^2 + y^2 = 25; 2x + y = 4")) == System(
        {
            System({Comparison(x, Term(Number(2))), Comparison(y, Term(Number(0)))}),
            System({Comparison(x, Term(Number(0))), Comparison(y, Term(Number(4)))}),
        }
    )


def test_solve_2_quadratic(processor, AST):
    assert processor.eval(AST("(x, y) -> x^2 + y^2 = 9; x^2 + 2y^2 = 9")) == System(
        {
            System({Comparison(x, Term(Number(3))), Comparison(y, Term(Number(0)))}),
            System({Comparison(x, Term(Number(-3))), Comparison(y, Term(Number(0)))}),
        }
    )
    assert processor.eval(AST("(x, y) -> x^2 + y^2 = 25; x^2 - 9 = y^2 - 2")) == System(
        {
            System({Comparison(x, Term(Number(-4))), Comparison(y, Term(Number(-3)))}),
            System({Comparison(x, Term(Number(-4))), Comparison(y, Term(Number(3)))}),
            System({Comparison(x, Term(Number(4))), Comparison(y, Term(Number(3)))}),
            System({Comparison(x, Term(Number(4))), Comparison(y, Term(Number(-3)))}),
        }
    )

    assert processor.eval(AST("(x, y) -> x^2 + 11 = 4y^2; (x^2 + y) = 28")) == System(
        {
            System(
                {
                    Comparison(x, Term(Number(5))),
                    Comparison(y, Term(Number(3))),
                }
            ),
            System({Comparison(x, Term(Number(-5))), Comparison(y, Term(Number(3)))}),
            System(
                {
                    Comparison(x, Term(Number(5, 2), Number(5), Number(1, 2))),
                    Comparison(y, Term(Number(-13, 4))),
                }
            ),
            System(
                {
                    Comparison(x, Term(Number(-5, 2), Number(5), Number(1, 2))),
                    Comparison(y, Term(Number(-13, 4))),
                }
            ),
        }
    )
