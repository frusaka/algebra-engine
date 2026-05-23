import pytest
from unittest.mock import patch

from datatypes import *
from solving.core import System, Comparison
from parsing import parser, AST
from parsing.parser import Function
from parsing.tokens import TokenType


@pytest.fixture
def mock_validate():
    with patch.object(Function, "validate", return_value=True):
        yield


def test_invalid():
    # Uses for-loop to avoid inflating test count
    for expr in ["9+", "-4+", "3()", "(()", ")", "()^2", "()()", "j6"]:
        with pytest.raises(SyntaxError):
            parser.parse(expr)


def test_spaced_numbers():
    for expr in ["3 4", "2 3y", "3 4+5", "3/4 5x"]:
        with pytest.raises(SyntaxError):
            AST(expr)


def test_unary(mock_validate):
    assert AST("-2") == Function("neg", 2)
    assert AST("-f") == Function("neg", "f")
    assert AST("+5") == Function("pos", 5)
    assert AST("+x") == Function("pos", "x")
    assert AST("--f") == Function("neg", Function("neg", "f"))


def test_binary(mock_validate):
    assert AST("2*3") == Function("mul", 2, 3)
    assert AST("2/3") == Function("div", 2, 3)
    assert AST("x+3") == Function("add", "x", 3)
    assert AST("x+z") == Function("add", "x", "z")
    assert AST("x=3") == Function("eq", "x", 3)
    assert AST("x>=3") == Function("ge", "x", 3)
    assert AST("x<=3") == Function("le", "x", 3)
    assert AST("x>3") == Function("gt", "x", 3)
    assert AST("x<3") == Function("lt", "x", 3)


def test_unary_vs_binary(mock_validate):
    assert AST("3+-5") == Function("add", 3, Function("neg", 5))
    assert AST("-5+3") == Function("add", Function("neg", 5), 3)
    assert AST("3++5") == Function("add", 3, Function("pos", 5))
    assert AST("3+++5") == Function("add", 3, Function("pos", Function("pos", 5)))
    assert AST("3--5") == Function("sub", 3, Function("neg", 5))
    assert AST("3---5") == Function("sub", 3, Function("neg", Function("neg", 5)))


def test_PEMDAS(mock_validate):
    # Basic operations
    assert AST("3+5*2") == Function("add", 3, Function("mul", 5, 2))
    assert AST("3-5/2") == Function("sub", 3, Function("div", 5, 2))
    assert AST("3/5*2") == Function("mul", Function("div", 3, 5), 2)
    assert AST("3*5/2") == Function("div", Function("mul", 3, 5), 2)

    # Exponentiation
    assert AST("3^5*2") == Function("mul", Function("pow", 3, 5), 2)
    assert AST("-3^5") == Function("neg", Function("pow", 3, 5))
    assert AST("(-3)^5") == Function("pow", Function("neg", 3), 5)
    assert AST("3^-5") == Function("pow", 3, Function("neg", 5))

    # Parentheses
    assert AST("(3+5)*2") == Function("mul", Function("add", 3, 5), 2)
    assert AST("3*(5+2)-8/4") == Function(
        "sub",
        Function("mul", 3, Function("add", 5, 2)),
        Function("div", 8, 4),
    )
    assert AST("3+(5*2-8)/4") == Function(
        "add",
        3,
        Function("div", Function("sub", Function("mul", 5, 2), 8), 4),
    )

    # s and coefficients
    assert AST("3x+5*2") == Function(
        "add",
        Function("mul", 3, "x"),
        Function("mul", 5, 2),
    )
    assert AST("3(x+5)*2") == Function(
        "mul",
        Function("mul", 3, Function("add", "x", 5)),
        2,
    )
    assert AST("2x^2 + 3x + 1") == Function(
        "add",
        Function(
            "add",
            Function("mul", 2, Function("pow", "x", 2)),
            Function("mul", 3, "x"),
        ),
        1,
    )

    # Comparisons and Comparisons
    assert AST("3+5=x") == Function("eq", Function("add", 3, 5), "x")
    assert AST("3=x+5") == Function("eq", 3, Function("add", "x", 5))
    assert AST("3+5=x") == Function("eq", Function("add", 3, 5), "x")
    assert AST("3<=x+5") == Function("le", 3, Function("add", "x", 5))


def test_monomial_special(mock_validate):
    assert AST("6a/8b") == Function(
        "div", Function("mul", 6, "a"), Function("mul", 8, "b")
    )
    assert AST("6/8b") == Function("div", 6, Function("mul", 8, "b"))
    assert AST("6/8*b") == Function("mul", Function("div", 6, 8), "b")
    assert AST("6a/8") == Function("div", Function("mul", 6, "a"), 8)
    assert AST("6a/8b^2") == Function(
        "div",
        Function("mul", 6, "a"),
        Function("mul", 8, Function("pow", "b", 2)),
    )


def test_functions(mock_validate):
    assert AST("subs(x-5,x=3)") == Function(
        "subs",
        Function("sub", "x", 5),
        Function("eq", "x", 3),
    )
    assert AST("approx(sqrt(7))") == Function(
        "approx", Function("sqrt", TokenType.NaN, 7)
    )
    assert AST("gcd(12,8, 10)") == Function("gcd", 12, 8, 10)
    assert AST("lcm(4,6)") == Function("lcm", 4, 6)
    assert AST("factor(x+5)") == Function("factor", Function("add", "x", 5))
    assert AST("expand(2(x+3))") == Function(
        "expand",
        Function("mul", 2, Function("add", "x", 3)),
    )
    assert AST("subs(x,2)+approx(2/3)") == Function(
        "add",
        Function("subs", "x", 2),
        Function("approx", Function("div", 2, 3)),
    )
    assert AST("2*factor(x)") == Function("mul", 2, Function("factor", "x"))
    assert AST("gcd(12,8)^2") == Function(
        "pow",
        Function("gcd", 12, 8),
        2,
    )


def test_system():
    with patch.object(Function, "validate", return_value=True):
        assert AST("[x=3, y=5]") == Function(
            "system",
            Function("eq", "x", 3),
            Function("eq", "y", 5),
        )
        assert AST("[x+y=10, x-y=2]") == Function(
            "system",
            Function("eq", Function("add", "x", "y"), 10),
            Function("eq", Function("sub", "x", "y"), 2),
        )
        assert AST("[2x+3y=12, x=4]") == Function(
            "system",
            Function(
                "eq",
                Function(
                    "add",
                    Function("mul", 2, "x"),
                    Function("mul", 3, "y"),
                ),
                12,
            ),
            Function("eq", "x", 4),
        )

    with pytest.raises(TypeError):
        parser.parse("[x>3, y=5]")

    with pytest.raises(SyntaxError):
        parser.parse("[x=3,]")


def test_validate_inputs():
    # Representation of all data types
    n = Const(1)
    x = Var("x")
    m = x * 2
    a = x + 2
    p = x**2
    c = Comparison(x, p)
    s = System([c, Comparison(n, a)])
    t = m, a
    # fmt: off
    bin_funcs = ["add", "sub", "mul", "div", "frac", "pow", "sqrt", "eq", "lt", "le", "gt", "ge"]
    un_funcs = ["factor", "expand", "neg", "pos", "approx"]
    inv_bin_pairs = [(n, c), (s, c), (c, s), (a, s), (s, a), (c, t), (t, c), (p, s), (s, p)]
    val_bin_pairs = [(n, n), (n, m), (m, n), (m, m), (a, n), (n, a), (a, a), (a, m), (m, a), (p, n), (n, p), (p, a), (a, p), (p, m), (m, p), (p, p)]
    # fmt: on
    # Validates binary operators
    for func in bin_funcs:
        # No argument Or passing None
        with pytest.raises(SyntaxError):
            Function(func)
        with pytest.raises(SyntaxError):
            Function(func, None)
        for i in inv_bin_pairs:
            # One argument
            with pytest.raises(SyntaxError):
                Function(func, i[0])
            with pytest.raises(TypeError):
                Function(func, *i)
        for i in val_bin_pairs:
            Function(func, *i)

    # Validates Unary operators
    for func in un_funcs:
        with pytest.raises(SyntaxError):
            Function(func)
        for i in [c, s, t]:
            with pytest.raises(TypeError):
                Function(func, i)
        for i in [n, x, m, a, p]:
            Function(func, i)

    # LCM and GCD
    for func in ["lcm", "gcd"]:
        with pytest.raises(SyntaxError):
            Function(func)
        for i, j in zip(inv_bin_pairs, val_bin_pairs):
            with pytest.raises(TypeError):
                Function(func, *i)
            with pytest.raises(TypeError):
                Function(func, *i, *j)
            Function(func, *j)
            Function(func, *j, *j)

    # Validates solve
    for i in (n, m, a, p, s, t, c):
        with pytest.raises(TypeError):
            Function("solve", s, i)
        with pytest.raises(TypeError):
            Function("solve", c, i)
    Function("solve", s, x)
    Function("solve", c, x)

    # Validates subsitution
    # for i in (x, n, m, a, p, s, c):
    #     Function("subs", i, c)
    #     Function("subs", i, c, *s)
    # with pytest.raises(SyntaxError):
    #     Function("subs")
    # with pytest.raises(TypeError):
    #     Function("subs", t)

    for i in val_bin_pairs:
        with pytest.raises(TypeError):
            Function("solve", *i)
        with pytest.raises(TypeError):
            Function("subs", *i)