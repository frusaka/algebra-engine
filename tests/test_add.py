import pytest
from datatypes.nodes import *
from parsing import parser
from collections import Counter

x = Var("x")
y = Var("y")


def test_divide_polynomial():
    assert (
        (Const(26, 5) * x**3 + 7 * x**2 - Const(156, 5) * x - 42)
        / (Const(7, 2) + Const(13, 5) * x)
    ).simplify() == Mul(Const(2), x**2 - 6)
    # Numerator with lower degrees
    assert (x - 1) / (x - 1) ** 2 == Pow(x - 1, -1)
    assert ((3 * (x - 4) - 7 * (x - 4)) / (x**2 - 8 * x + 16)).simplify() == Mul(
        Const(-4), Pow(x - 4, -1)
    )
    assert ((3 * (x + 6) - (x + 6) / 2) / (x + 6) ** 2) == Mul(
        Const(5, 2), (x + 6) ** -1
    )
    assert (
        parser.eval("(0.3x^2 + 2.4x + 4.5) / (0.2x^3 + 0.6x^2 - 5x - 15)").simplify()
        == Const(3, 2) * (x - 5) ** -1
    )

    assert parser.eval(
        "(x^2 + 0.4x - 7.8) / (x^3 - 8.2x^2 + 22.36x - 20.28)"
    ).simplify() == Mul(
        Const(5),
        Add(x, Const(3)),
        Pow(
            Mul((x - 3), (5 * x - 13)),
            Const(-1),
        ),
    )

    # Division with Remainder : Engine no longer outputs mixed Adds
    # Coming back soon
    # assert parser.eval("(-6x^2 + 2x + 20)/(2-2x)")
    # assert parser.eval("(4x^2 - 17.64) / (2x - 4)")
    assert (((x - 3) * (x + 5) + (x - 3)) / ((x - 3) * (x + 5))).simplify() == Mul(
        x + 6, Pow(x + 5, Const(-1))
    )

    assert ((x**2 - 4) / (x**2 + 8 * x - 20)).simplify() == Mul(x + 2, Pow(x + 10, -1))


def test_divide_multivariate():
    a = Var("a")
    b = Var("b")
    c = Var("c")
    d = Var("d")
    assert ((3 * a + 3 * b) / (a + b)) == 3
    assert ((a**3 + b**3) / (a + b)).simplify() == Add(b**2, a**2, Mul(Const(-1), a, b))

    assert parser.eval("(-3.75c^2 + 18ab + 4.5abc - 15c)/(3+0.75c)").simplify() == Add(
        6 * a * b, -5 * c
    )

    assert ((a * b / (x + 5)) * ((x**2 + x - 20) / (c * d))).simplify() == Mul(
        a, b, (x - 4), Pow(c * d, Const(-1))
    )


def test_multiply_polynomial():
    # Multiplying univariate polynomials
    assert ((2 * x + 3) * (x / 2 - 5)).expand() == Add(x**2, -17 * x / 2, Const(-15))

    assert Mul((x + 1), (x + 2), (x + 3)).expand() == Add(
        x**3, 6 * x**2, 11 * x, Const(6)
    )

    # Multiplying multivariate polynomials
    assert Mul((x + 1), (y + 2)).expand() == Add(x * y, 2 * x, y, Const(2))

    # Multiplication containing a fraction
    assert Mul((x - 4 + 12 / (x + 4)), (x + 4)).expand() == Add(x**2, Const(-4))

    # Nested
    assert (((y + 3) * (y - 3)) ** 2).expand() == Add(y**4, -18 * y**2, Const(81))

    # Negative Exponents
    assert Mul((x + 1) ** -1, (x**2 + 2 * x + 1)).expand() == Add(x, Const(1))

    assert ((x / 3 - Const(7, 3)) * x**-2) == Mul(Const(1, 3), Add(x, Const(-7)), x**-2)

    # Consinstency regardless of the order
    expected = Add(3 * x * y, -4 * y)
    assert parser.eval("(x+2)^-1(3x-4)(xy+2y)").expand() == expected
    assert parser.eval("(3x-4)(x+2)^-1(xy+2y)").expand() == expected
    assert parser.eval("(xy+2y)(3x-4)(x+2)^-1").expand() == expected


def test_multiply_rationals():
    # Multiplying Polynomial rationals
    assert (
        (x**4 - 25 * x**2)
        / (x**2 + 8 * x + 15)
        * ((x**2 + 2 * x - 3) / (6 * x**3 - 36 * x**2 + 30 * x))
    ).simplify() == x / 6
    assert (
        ((2 * x**4 - 8 * x**2) / (x**4 - 10 * x**3))
        * ((x + 7) / (4 * x**2 + 36 * x + 56))
    ).simplify() == Mul(Const(1, 2), x - 2, x**-1, Pow(x - 10, Const(-1)))

    assert (
        ((x**3 - 6 * x**2 - 7 * x) / (3 * x + 27))
        * ((x**2 - 81) / (x**5 - 8 * x**4 - 9 * x**3))
    ).simplify() == Mul(Const(1, 3), x - 7, x**-2)

    assert (
        (
            ((x**2 - 49) / (x**2 + x - 56))
            * ((6 * x**4 - 54 * x**3) / (2 * x**4 - 4 * x**3 - 126 * x**2))
        )
    ).simplify() == Mul(Const(3), x, (x + 8) ** -1)
    assert ((x**2 - 25) / ((x - 5) / (x + 10))).simplify() == Mul(x + 5, x + 10)

    assert (
        -9
        * x
        / (x**2 - 8 * x)
        * (9 * x**3 + 36 * x**2 - 189 * x)
        / (x**2 - 10 * x + 21)
        / ((x + 7) / (x**2 - 15 * x + 56))
    ).simplify() == -81 * x
    assert (
        (24 - 6 * x)
        / (x**2 - 10 * x + 24)
        * (x**2 - 8 * x + 12)
        / (10 - x)
        / ((x**2 + 8 * x - 20) / (100 * x - x**3))
    ).simplify() == -6 * x
    assert (
        (-x - 6)
        / (x + 9)
        * (x + 10)
        / (-2 * x - 18)
        / ((x**2 + 16 * x + 60) / (x**2 + 18 * x + 81))
    ).simplify() == Const(1, 2)

    assert (
        ((x**2 - 4) / (x**2 + 4 * x + 4)) * ((x**3 + 8) / (x**3 - 2 * x**2 - 4 * x + 8))
    ).simplify() == Mul(
        Add(x**2, -2 * x, Const(4)), Pow(Mul(x + 2, x - 2), exp=Const(-1))
    )


@pytest.mark.skip
def test_add_rationals():
    pass


def test_merge():
    z = Var("z")
    # Like terms with multiple variables
    assert Counter(Add.merge([2 * x, 3 * x])) == Counter([5 * x])
    assert Counter(Add.merge([5 * y, -3 * y])) == Counter([2 * y])
    assert Counter(Add.merge([x, y, z, x, y, z])) == Counter(
        [Mul(Const(2), x), Mul(Const(2), y), Mul(Const(2), z)]
    )

    # No like terms
    assert Counter(Add.merge([x, y, z])) == Counter([x, y, z])
    assert Counter(Add.merge([x**2, y**2])) == Counter([x**2, y**2])
    assert Counter(Add.merge([-2 * z, -3 * z])) == Counter([-5 * z])

    # Multiple like terms and constants
    assert Counter(Add.merge([x, 2 * x, Const(3), Const(4), -x])) == Counter([2 * x, 7])

    # Multiple variables and powers
    assert Counter(Add.merge([x**2, 2 * x**2, z**2, -(z**2)])) == Counter([3 * x**2])
    assert Counter(Add.merge([x**3, 2 * x**3, z**3, 3 * z**3])) == Counter(
        [3 * x**3, 4 * z**3]
    )
    # Zero result
    assert Counter(Add.merge([z, -z])) == Counter([0])
    assert Counter(Add.merge([x**2, -(x**2)])) == Counter([0])
    # Constants only
    assert Counter(Add.merge([Const(1), Const(2), Const(3)])) == Counter([6])
