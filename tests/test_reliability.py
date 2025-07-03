import pytest
from datatypes.nodes import Add, Mul, Const, Var


def test_const_equality_and_hash():
    c1 = Const(5)
    c3 = Const(7)
    c4 = Const(2, 3)
    c5 = Const(2, 3)
    c6 = Const(1, 5)
    assert c1 == 5
    assert c1 != c3
    assert c4 == c5
    assert c4 != c6
    assert hash(c1) == 5
    assert hash(c4) == hash(c5)


def test_const_equality_and_hash_extended():
    c1 = Const(5)
    c2 = Const(5)
    c3 = Const(7)
    c4 = Const(2, 3)
    c5 = Const(2, 3)
    c6 = Const(1, 5)
    assert c1 == c2
    assert c1 != c3
    assert c4 == c5
    assert c4 != c6
    assert hash(c1) == 5
    assert hash(c4) == hash(c5)
    # Hashes should match Python native numbers
    assert hash(c1) == hash(5)
    assert hash(Const(1, 2)) == hash(0.5)
    assert hash(Const(-3, 4)) == hash(-0.75)
    assert hash(Const(3, 2)) == hash(1.5)
    assert hash(Const(2 - 3j)) == hash(2 - 3j)
    assert hash(Const(2 + 3j, 3)) != hash((2 + 3j) / 3)
    # Comparison checks for non-integer denominators
    assert Const(2, 3) > Const(1, 5)
    assert Const(1, 2) < Const(3, 4)
    assert Const(7, 2) >= Const(7, 2)
    assert Const(5, 6) <= Const(5, 6)


def test_add_equality_and_hash():
    a1 = Add(Const(2), Var("x"))
    a2 = Add(Const(2), Var("x"))
    a3 = Add(Var("x"), Const(2))
    a4 = Add(Const(3), Var("x"))
    a5 = Add(Const(2), Var("y"))
    m1 = Mul(Const(2), Var("x"))
    assert a1 == a2
    assert hash(a1) == hash(a2)
    assert a1 != a4
    assert a1 != a5
    assert hash(a1) != hash(a4)
    assert hash(a1) != hash(a5)
    assert a1 == a3
    assert hash(a1) == hash(a3)
    # Cross-type equality
    assert a1 != m1
    assert hash(a1) != hash(m1)
    assert a1 != Const(2)
    assert a1 != Var("x")


def test_mul_equality_and_hash():
    m1 = Mul(Const(2), Var("x"))
    m2 = Mul(Const(2), Var("x"))
    m3 = Mul(Var("x"), Const(2))  # If Mul is commutative, these should be equal
    m4 = Mul(Const(3), Var("x"))
    m5 = Mul(Const(2), Var("y"))
    a1 = Add(Const(2), Var("x"))
    assert m1 == m2
    assert hash(m1) == hash(m2)
    assert m1 != m4
    assert m1 != m5
    assert hash(m1) != hash(m4)
    assert hash(m1) != hash(m5)
    assert m1 == m3
    assert hash(m1) == hash(m3)
    # Cross-type equality
    assert m1 != a1
    assert hash(m1) != hash(a1)
    assert m1 != Const(2)
    assert m1 != Var("x")


def test_nested_nodes_equality_and_hash():
    expr1 = Add(Mul(Const(2), Var("x")), Const(3))
    expr2 = Add(Mul(Const(2), Var("x")), Const(3))
    expr3 = Add(Const(3), Mul(Const(2), Var("x")))
    expr4 = Add(Mul(Const(2), Var("y")), Const(3))
    expr5 = Mul(Add(Const(2), Var("x")), Const(3))
    assert expr1 == expr2
    assert hash(expr1) == hash(expr2)
    assert expr1 != expr4
    assert hash(expr1) != hash(expr4)
    # If Add is commutative, uncomment the next two lines:
    assert expr1 == expr3
    assert hash(expr1) == hash(expr3)
    # Cross-type equality
    assert expr1 != expr5
    assert hash(expr1) != hash(expr5)
