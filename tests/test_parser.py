import pytest
from parsing import parser
from parsing import parser, TokenType, AST


def test_invalid():
    # Uses for-loop to avoid inflating test count
    for expr in ["9+", "-4+", "3()", "(()", ")", "()^2", "()()", "j6"]:
        with pytest.raises(SyntaxError):
            parser.eval(expr)


def test_spaced_numbers():
    for expr in ["3 4", "2 3y", "3 4+5", "3/4 5x"]:
        with pytest.raises(SyntaxError):
            parser.eval(expr)


def test_unary():
    assert AST("-2") == (TokenType.NEG, 2)
    assert AST("-f") == (TokenType.NEG, "f")
    assert AST("+5") == (TokenType.POS, 5)
    assert AST("+x") == (TokenType.POS, "x")
    assert AST("--f") == (TokenType.NEG, TokenType.NEG, "f")


def test_binary():
    assert AST("2*3") == (TokenType.MUL, 2, 3)
    assert AST("2/3") == (TokenType.TRUEDIV, 2, 3)
    assert AST("x+3") == (TokenType.ADD, "x", 3)
    assert AST("x+z") == (TokenType.ADD, "x", "z")
    assert AST("x=3") == (TokenType.EQ, "x", 3)
    assert AST("x>=3") == (TokenType.GE, "x", 3)
    assert AST("x<=3") == (TokenType.LE, "x", 3)
    assert AST("x>3") == (TokenType.GT, "x", 3)
    assert AST("x<3") == (TokenType.LT, "x", 3)


def test_unary_vs_binary():
    assert AST("3+-5") == (
        TokenType.ADD,
        3,
        TokenType.NEG,
        5,
    )
    assert AST("-5+3") == (TokenType.ADD, TokenType.NEG, 5, 3)
    assert AST("3++5") == (TokenType.ADD, 3, TokenType.POS, 5)
    assert AST("3+++5") == (TokenType.ADD, 3, TokenType.POS, TokenType.POS, 5)
    assert AST("3--5") == (TokenType.SUB, 3, TokenType.NEG, 5)
    assert AST("3---5") == (TokenType.SUB, 3, TokenType.NEG, TokenType.NEG, 5)


def test_PEMDAS():
    # Basic operations
    assert AST("3+5*2") == (TokenType.ADD, 3, TokenType.MUL, 5, 2)
    assert AST("3-5/2") == (TokenType.SUB, 3, TokenType.TRUEDIV, 5, 2)
    assert AST("3/5*2") == (TokenType.MUL, TokenType.TRUEDIV, 3, 5, 2)
    assert AST("3*5/2") == (TokenType.TRUEDIV, TokenType.MUL, 3, 5, 2)

    # Exponentiation
    assert AST("3^5*2") == (TokenType.MUL, TokenType.POW, 3, 5, 2)
    assert AST("-3^5") == (TokenType.NEG, TokenType.POW, 3, 5)
    assert AST("(-3)^5") == (TokenType.POW, TokenType.NEG, 3, 5)
    assert AST("3^-5") == (TokenType.POW, 3, TokenType.NEG, 5)

    # Parentheses
    assert AST("(3+5)*2") == (TokenType.MUL, TokenType.ADD, 3, 5, 2)
    assert AST("3*(5+2)-8/4") == (
        TokenType.SUB,
        TokenType.MUL,
        3,
        TokenType.ADD,
        5,
        2,
        TokenType.TRUEDIV,
        8,
        4,
    )
    assert AST("3+(5*2-8)/4") == (
        TokenType.ADD,
        3,
        TokenType.TRUEDIV,
        TokenType.SUB,
        TokenType.MUL,
        5,
        2,
        8,
        4,
    )

    # s and coefficients
    assert AST("3x+5*2") == (
        TokenType.ADD,
        TokenType.MUL,
        3,
        "x",
        TokenType.MUL,
        5,
        2,
    )
    assert AST("3(x+5)*2") == (
        TokenType.MUL,
        TokenType.MUL,
        3,
        TokenType.ADD,
        "x",
        5,
        2,
    )
    assert AST("2x^2 + 3x + 1") == (
        TokenType.ADD,
        TokenType.ADD,
        TokenType.MUL,
        2,
        TokenType.POW,
        "x",
        2,
        TokenType.MUL,
        3,
        "x",
        1,
    )

    # Comparisons and Comparisons
    assert AST("3+5=x") == (TokenType.EQ, TokenType.ADD, 3, 5, "x")
    assert AST("3=x+5") == (TokenType.EQ, 3, TokenType.ADD, "x", 5)
    assert AST("3+5=x") == (TokenType.EQ, TokenType.ADD, 3, 5, "x")
    assert AST("3<=x+5") == (TokenType.LE, 3, TokenType.ADD, "x", 5)


def test_monomial_special():
    assert AST("6a/8b") == (
        TokenType.TRUEDIV,
        TokenType.MUL,
        6,
        "a",
        TokenType.MUL,
        8,
        "b",
    )
    assert AST("6/8b") == (TokenType.TRUEDIV, 6, TokenType.MUL, 8, "b")
    assert AST("6/8*b") == (TokenType.MUL, TokenType.TRUEDIV, 6, 8, "b")
    assert AST("6a/8") == (TokenType.TRUEDIV, TokenType.MUL, 6, "a", 8)
    assert AST("6a/8b^2") == (
        TokenType.TRUEDIV,
        TokenType.MUL,
        6,
        "a",
        TokenType.MUL,
        8,
        TokenType.POW,
        "b",
        2,
    )
