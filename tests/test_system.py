from data_types import *


def test_solve_linear(processor, AST):
    v = Variable("v")
    w = Variable("w")
    x = Variable("x")
    y = Variable("y")
    z = Variable("z")

    # Basic system of two equations
    assert System(
        {
            processor.eval(AST("x + y = 5")),
            processor.eval(AST("3x = 4y + 1")),
        }
    )[x, y] == System(
        {
            Comparison(Term(value=x), Term(Number(3))),
            Comparison(Term(value=y), Term(Number(2))),
        }
    )
    assert System(
        {
            processor.eval(AST("2x + 3y = 7")),
            processor.eval(AST("x - y = 2")),
        }
    )[x, y] == System(
        {
            Comparison(Term(value=x), Term(Number(13, 5))),
            Comparison(Term(value=y), Term(Number(3, 5))),
        }
    )
    assert System(
        {
            processor.eval(AST("2x - 3 = 5y + 7")),
            processor.eval(AST("4x + 2y = 14")),
        }
    )[x, y] == System(
        {
            Comparison(Term(value=x), Term(Number(15, 4))),
            Comparison(Term(value=y), Term(Number(-1, 2))),
        }
    )

    # System of 3 equations
    assert System(
        {
            processor.eval(AST("2x - y + 3z = 5")),
            processor.eval(AST("x + 4y - 2z = 6")),
            processor.eval(AST("3x + 2y + z = 8")),
        }
    )[x, y, z] == System(
        {
            Comparison(Term(value=x), Term(Number(-2, 7))),
            Comparison(Term(value=y), Term(Number(3))),
            Comparison(Term(value=z), Term(Number(20, 7))),
        }
    )
    assert System(
        {
            processor.eval(AST("x + 2y - z = 4")),
            processor.eval(AST("3x - y + 4z = 10")),
            processor.eval(AST("2x + 3y + z = 7")),
        }
    )[x, y, z] == System(
        {
            Comparison(Term(value=x), Term(Number(53, 14))),
            Comparison(Term(value=y), Term(Number(-1, 14))),
            Comparison(Term(value=z), Term(Number(-5, 14))),
        }
    )

    # Advanced: System of 5 equations
    assert System(
        {
            processor.eval(AST("x + 2y - z + w + 3v = 10")),
            processor.eval(AST("2x - y + 3z - 2w + v = -5")),
            processor.eval(AST("3x + 4y + 2z + w - v = 12")),
            processor.eval(AST("x - 3y + 4z + 2w + 5v = 7")),
            processor.eval(AST("-2x + y - 3z + w + 4v = -8")),
        }
    )[v, w, x, y, z] == System(
        {
            Comparison(Term(value=v), Term(Number(-43, 32))),
            Comparison(Term(value=w), Term(Number(201, 32))),
            Comparison(Term(value=x), Term(Number(421, 40))),
            Comparison(Term(value=y), Term(Number(-131, 32))),
            Comparison(Term(value=z), Term(Number(-433, 80))),
        }
    )
