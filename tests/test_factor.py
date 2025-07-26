from datatypes.mul import Mul
from utils import factor
from datatypes.nodes import Var, Const

x = Var("x")
y = Var("y")
a = Var("a")
b = Var("b")


# Univariate tests
def test_factor_univariate():
    expr = (x + 1) * (3 * x + 7)
    expanded = expr.expand()
    assert not expr == expanded and factor(expanded) == expr
    expr = (2 * x**2 - 8) * (x**3 - 8) ** 4 * (x**2 + x - 56) * (x - 5) * (x - 1)
    expanded = expr.expand()
    assert not expr == expanded and factor(expanded) == 2 * Mul(
        x + 8, x - 7, x + 2, x - 5, x - 1, (x - 2) ** 5, (x**2 + 2 * x + 4) ** 4
    )


def test_factor_multivariate():
    assert factor(a**4 - b**4) == Mul(a + b, a - b, a**2 + b**2)
    assert factor(-3 * y**2 - 3 * x * y + 2 * a * y + 2 * a * x) == Mul(
        2 * a - 3 * y, x + y
    )
    assert factor(
        ((52 * x**3 + 70 * x**2 - 312 * x - 420) * (a**3 - b**3)).expand()
    ) == Mul(Const(2), 26 * x + 35, a - b, x**2 - 6, a**2 + b**2 + a * b)
    expr = (
        (a**2 + b**2 + 2 * a * b)
        * (a - 2 * b) ** 2
        * (x**3 - 8) ** 2
        * (b - 2 * x) ** 3
        * (x - b)
    ).expand()
    factored = factor(expr)
    assert factored != expr and factored.expand() == expr
