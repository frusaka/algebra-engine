import pytest
from datatypes.nodes import Const, Var, Mul, Add
from collections import Counter

x = Var("x")
a = Var("a")
b = Var("b")
y = Var("y")

def test_merge_variables_flatten():
    # flatten and compare Counters for both sides
    assert Counter(Mul.flatten(8 * x / (12 * x**2 * b))) == Counter(
        Mul.flatten(Const(2, 3) * x**-1 * b**-1)
    )
    assert Counter(Mul.flatten((x * y) / 1)) == Counter([x, y])
    assert Counter(Mul.flatten((2 * x) / y)) == Counter([Const(2), x, y**-1])
    assert Counter(Mul.flatten((3 * x * y) / (3 * x * y))) == Counter([Const(1)])
    assert Counter(Mul.flatten((4 * x) / -2)) == Counter([Const(-2), x])
    assert Counter(Mul.flatten((x**3 * y**2) / (x * y))) == Counter([x**2, y])
    assert Counter(Mul.flatten((5 * x**2 * b) / (10 * a * x * b))) == Counter(
        [Const(1, 2), x, a**-1]
    )
    assert Counter(Mul.flatten((6 * a * b) / (8 * a))) == Counter([Const(3, 4), b])
    assert Counter(Mul.flatten((3 * a * b) / (b / 10))) == Counter([Const(30), a])
    assert Counter(Mul.flatten((6 * a * b) / (8 * a * b))) == Counter([Const(3, 4)])

    # Additive factors
    assert Counter(Mul.flatten(((x + y) * x) / x)) == Counter([x + y])
    assert Counter(Mul.flatten(((x + y) * (a + b)) / (x + y))) == Counter([a + b])
    assert Counter(Mul.flatten((x + y) / (x + y))) == Counter([Const(1)])
    assert Counter(Mul.flatten((Const(2) * (x + y) * a) / (a * (x + y)))) == Counter(
        [Const(2)]
    )
    assert Counter(Mul.flatten((Const(2) * Add(x, y) * x) / (Const(4) * x))) == Counter(
        [Const(1, 2), x + y]
    )
    assert Counter(Mul.flatten((x + y) * (a + b) * Const(0))) == Counter([Const(0)])
    assert Counter(Mul.flatten(((x + y) * (a + b)) / Const(1))) == Counter(
        [x + y, a + b]
    )
    assert Counter(Mul.flatten(((x + y) * Add(a, b) * x) / (x * Add(a, b)))) == Counter(
        [x + y]
    )
    assert Counter(
        Mul.flatten((Const(3) * Add(x, y) * (a + b)) / (Const(3) * Add(x, y)))
    ) == Counter([a + b])
    assert Counter(Mul.flatten((Add(x, y) ** 2) / Add(x, y))) == Counter([x + y])
    assert Counter(Mul.flatten(((x + y) ** 3) / ((x + y) ** 2))) == Counter([x + y])
    assert Counter(Mul.flatten(((x + y) ** 5) / ((x + y) ** 5))) == Counter([Const(1)])
    assert Counter(
        Mul.flatten(((x + y) ** 4 * Add(a, b) ** 2) / ((x + y) ** 2 * Add(a, b)))
    ) == Counter([(x + y) ** 2, a + b])
    assert Counter(Mul.flatten(((x + y) ** 2 * (a + b)) / (x + y))) == Counter(
        [x + y, a + b]
    )


def test_merge_variables_merge():
    # tests for Mul.merge
    assert Counter(Mul.merge([x, y, Const(1) ** -1])) == Counter([x, y])
    assert Counter(Mul.merge([Const(2), x, y**-1])) == Counter([Const(2), x, y**-1])
    assert Counter(
        Mul.merge([Const(3), x, y, Const(3) ** -1, x**-1, y**-1])
    ) == Counter([Const(1)])
    assert Counter(Mul.merge([Const(4), x, Const(-2) ** -1])) == Counter([Const(-2), x])
    assert Counter(Mul.merge([x**3, y**2, x**-1, y**-1])) == Counter([x**2, y])
    assert Counter(
        Mul.merge([Const(5), x**2, b, Const(10) ** -1, a**-1, x**-1, b**-1])
    ) == Counter([Const(1, 2), x, a**-1])
    assert Counter(Mul.merge([Const(6), a, b, Const(8) ** -1, a**-1])) == Counter(
        [Const(3, 4), b]
    )
    assert Counter(Mul.merge([Const(3), a, b, Const(1, 10) ** -1, b**-1])) == Counter(
        [Const(30), a]
    )
    assert Counter(
        Mul.merge([Const(6), a, b, Const(8) ** -1, a**-1, b**-1])
    ) == Counter([Const(3, 4)])


def test_merge_variables_zero_division():
    with pytest.raises(ZeroDivisionError):
        Mul.merge([x, y, Const(0) ** -1])
    with pytest.raises(ZeroDivisionError):
        Mul.flatten((x * y) / 0)
