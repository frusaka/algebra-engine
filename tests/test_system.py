from datatypes.nodes import *
from solving.core import solve
from solving.system import System
from solving.comparison import Comparison, CompRel
from solving.solutions import SolutionSet
from solving.eval_trace import (
    ETBranchNode,
    ETNode,
    ETSteps,
    ETOperatorNode,
    ETSubNode,
    ETTextNode,
    ETVerifyNode,
)
from parsing import parser
from solving.utils import nth_roots

v = Var("v")
w = Var("w")
x = Var("x")
y = Var("y")
z = Var("z")


def test_records_steps():
    system = System([Comparison(x + y, Const(5)), Comparison(3 * x + 4 * y, 4 * y + 1)])
    solve(system)
    steps = ETSteps.data
    # Labels the process
    assert type(steps[0]) is ETTextNode
    assert steps[0].result == "Solving for x, y"
    # Shows the original system
    assert type(steps[1]) is ETNode
    assert steps[1].result is system
    # Might do groebner business, so we can't simply go with steps[2]
    # Branches out
    br = next(i for i in steps if type(i) is list)
    assert type(br[0]) is ETTextNode
    assert "Solve for " in br[0].result

    # Substitutes
    assert type(br[-2]) is ETSubNode
    assert br[-2].old == br[0].result[-1]
    # Another brach
    br_2 = next(i for i in steps if type(i) is list and i is not br)
    # Solves for the other variable
    assert br_2[0].result != br[0].result
    # Verifies solution
    assert type(steps[-2]) is ETTextNode
    assert steps[-2].result == "Verifying solutions"
    # Validates a correct solution
    assert type(steps[-1]) is ETVerifyNode
    assert type(steps[-1].result) is ETBranchNode
    assert steps[-1].state


def test_solve_linear():
    # Basic system of two equations
    assert parser.eval("[x + y = 5, 3x = 4y + 1]") == Comparison((x, y), (3, 2))
    assert parser.eval("[2x + 3y = 7, x - y = 2]") == Comparison(
        (x, y), (Const(13, 5), Const(3, 5))
    )
    assert parser.eval("[2x - 3 = 5y + 7, 2x + 2y = 14]") == Comparison(
        (x, y), (Const(45, 7), Const(4, 7))
    )

    # System of 3 equations
    assert (
        parser.eval(
            """
            [2x - y + 3z = 5,
            x + 4y - 2z = 6,
            3x + 2y + z = 8]
            """
        )
        == Comparison((x, y, z), (Const(-2, 7), 3, Const(20, 7)))
    )
    assert (
        parser.eval(
            """
            [x + 2y - z = 4,
            3x - y + 4z = 10,
            2x + 3y + z = 7]
            """
        )
        == Comparison(
            (x, y, z),
            (Const(53, 14), Const(-1, 14), Const(-5, 14)),
        )
    )
    # Advanced: System of 5 equations
    assert (
        parser.eval(
            """
            [
            x + 2y - z + w + 3v = 10,
            2x - y + 3z - 2w + v = -5,
            3x + 4y + 2z + w - v = 12,
            x - 3y + 4z + 2w + 5v = 7,
            -2x + y - 3z + w + 4v = -8]
            """
        )
        == Comparison(
            (v, w, x, y, z),
            (
                Const(-43, 32),
                Const(201, 32),
                Const(421, 40),
                Const(-131, 32),
                Const(-433, 80),
            ),
        )
    )


def test_solve_quadratic_linear():
    assert parser.eval("[v + w = 10, vw = 21]") == Comparison(
        (v, w), SolutionSet({(3, 7), (7, 3)}), CompRel.IN
    )
    assert parser.eval("[y = x^2 - 3x - 46, y = -3x + 3]") == Comparison(
        (x, y), SolutionSet({(-7, 24), (7, -18)}), CompRel.IN
    )
    assert parser.eval("[y = x^2 - 19x + 58, y = -3x - 5]") == Comparison(
        (x, y),
        SolutionSet(
            {
                (9, -32),
                (7, -26),
            }
        ),
        CompRel.IN,
    )
    assert parser.eval("[(x - 2)^2 + y^2 = 58, x + y = -2]") == Comparison(
        (x, y), SolutionSet({(5, -7), (-5, 3)}), CompRel.IN
    )
    assert parser.eval("[(x + 3)^2 + y^2 = 25, 2x + y = 4]") == Comparison(
        (x, y), SolutionSet({(2, 0), (0, 4)}), CompRel.IN
    )
    assert parser.eval("[xy = z, x + y = -7, x + z = -3y - 1]") == Comparison(
        (x, y, z), SolutionSet({(-4, -3, 12), (-5, -2, 10)}), CompRel.IN
    )


def test_solve_2_quadratic():
    assert parser.eval("[x^2 + y^2 = 9, x^2 + 2y^2 = 9]") == Comparison(
        (x, y),
        SolutionSet(
            {
                (3, 0),
                (-3, 0),
            }
        ),
        CompRel.IN,
    )
    assert parser.eval("[x^2 + y^2 = 25, x^2 - 9 = y^2 - 2]") == Comparison(
        (x, y), SolutionSet({(-4, -3), (-4, 3), (4, -3), (4, 3)}), CompRel.IN
    )

    assert parser.eval("[x^2 + 11 = 4y^2, (x^2 + y) = 28]") == Comparison(
        (x, y),
        SolutionSet(
            {
                (5, 3),
                (-5, 3),
                (Const(5, 2) * 5 ** Const(1, 2), Const(-13, 4)),
                (Const(-5, 2) * 5 ** Const(1, 2), Const(-13, 4)),
            }
        ),
        CompRel.IN,
    )


def test_solve_high_degree():
    assert parser.eval(
        "[x + y + z = 1, x^2 + y^2 + z^2 = 1, x^3 + y^3 + z^3 = 1]"
    ) == Comparison(
        (x, y, z),
        SolutionSet(
            {
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1),
            }
        ),
        CompRel.IN,
    )

    # The solutions are irational, just check that it finds something

    # Base: x = -1, x = (1 ± √5)/2
    assert getvar(parser.eval("[x^2 + y^2 + z^2 = 4, xyz = 1, x + y + z = 0]"), x) == {
        -1,
        Mul.from_terms([(1 + Const(5) ** 0.5), Const(1, 2)], 0),
        Mul.from_terms([(1 - Const(5) ** 0.5), Const(1, 2)], 0),
    }
    # Base: c = unity cuberoots of 3, etc
    assert getvar(
        parser.eval("[abc = 6, a^2 + b^2 = 6, a^2 + b^2 + c^3 = 9]"), "c"
    ) == nth_roots({Const(3)}, 3)

    # exact values and approximate values
    assert getvar(parser.eval("[x^4 + y^2 = 5, yx^3 = 2]"), y, 4) == {
        2,
        -2,
        -0.6374,
        0.6374,
        0.5705j,
        -0.5705j,
        2.3409 + 0.1421j,
        2.3409 - 0.1421j,
        -2.3409 + 0.1421j,
        -2.3409 - 0.1421j,
    }


def round_(n, ndigits):
    if n.imag:
        return complex(round(n.real, ndigits), round(n.imag, ndigits))
    return round(n, ndigits)


def getvar(s, v, ndigits=None):
    res = {i[idx] for i in s.right for idx in range(len(s.left)) if s.left[idx] == v}
    print(res)
    if ndigits is not None:
        return {round_(i.approx(), ndigits) for i in res}
    return res
