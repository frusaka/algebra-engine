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
            AST(expr)


def test_unary():
    assert AST("-2") == (TokenType.NEG, 2)
    assert AST("-f") == (TokenType.NEG, "f")
    assert AST("+5") == (TokenType.POS, 5)
    assert AST("+x") == (TokenType.POS, "x")
    assert AST("--f") == (TokenType.NEG, TokenType.NEG, "f")


def test_binary():
    assert AST("2*3") == (TokenType.MUL, 2, 3)
    assert AST("2/3") == (TokenType.DIV, 2, 3)
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
    assert AST("3-5/2") == (TokenType.SUB, 3, TokenType.DIV, 5, 2)
    assert AST("3/5*2") == (TokenType.MUL, TokenType.DIV, 3, 5, 2)
    assert AST("3*5/2") == (TokenType.DIV, TokenType.MUL, 3, 5, 2)

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
        TokenType.DIV,
        8,
        4,
    )
    assert AST("3+(5*2-8)/4") == (
        TokenType.ADD,
        3,
        TokenType.DIV,
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
        TokenType.DIV,
        TokenType.MUL,
        6,
        "a",
        TokenType.MUL,
        8,
        "b",
    )
    assert AST("6/8b") == (TokenType.DIV, 6, TokenType.MUL, 8, "b")
    assert AST("6/8*b") == (TokenType.MUL, TokenType.DIV, 6, 8, "b")
    assert AST("6a/8") == (TokenType.DIV, TokenType.MUL, 6, "a", 8)
    assert AST("6a/8b^2") == (
        TokenType.DIV,
        TokenType.MUL,
        6,
        "a",
        TokenType.MUL,
        8,
        TokenType.POW,
        "b",
        2,
    )


def test_functions():
    assert AST("subs(x-5,x=3)") == (
        TokenType.SUBS,
        TokenType.COMMA,
        TokenType.SUB,
        "x",
        5,
        TokenType.EQ,
        "x",
        3,
    )
    assert AST("approx(sqrt(7))") == (TokenType.APPROX, TokenType.SQRT, 7)
    assert AST("gcd(12,8, 10)") == (
        TokenType.GCD,
        TokenType.COMMA,
        TokenType.COMMA,
        12,
        8,
        10,
    )
    assert AST("lcm(4,6)") == (TokenType.LCM, TokenType.COMMA, 4, 6)
    assert AST("factor(x+5)") == (TokenType.FACTOR, TokenType.ADD, "x", 5)
    assert AST("expand(2(x+3))") == (
        TokenType.EXPAND,
        TokenType.MUL,
        2,
        TokenType.ADD,
        "x",
        3,
    )
    assert AST("subs(x,2)+approx(2/3)") == (
        TokenType.ADD,
        TokenType.SUBS,
        TokenType.COMMA,
        "x",
        2,
        TokenType.APPROX,
        TokenType.DIV,
        2,
        3,
    )
    assert AST("2*factor(x)") == (TokenType.MUL, 2, TokenType.FACTOR, "x")
    assert AST("gcd(12,8)^2") == (
        TokenType.POW,
        TokenType.GCD,
        TokenType.COMMA,
        12,
        8,
        2,
    )


def test_system():
    assert AST("[x=3, y=5]") == (
        TokenType.LBRACK,
        TokenType.COMMA,
        TokenType.EQ,
        "x",
        3,
        TokenType.EQ,
        "y",
        5,
    )
    assert AST("[x+y=10, x-y=2]") == (
        TokenType.LBRACK,
        TokenType.COMMA,
        TokenType.EQ,
        TokenType.ADD,
        "x",
        "y",
        10,
        TokenType.EQ,
        TokenType.SUB,
        "x",
        "y",
        2,
    )
    assert AST("[2x+3y=12, x=4]") == (
        TokenType.LBRACK,
        TokenType.COMMA,
        TokenType.EQ,
        TokenType.ADD,
        TokenType.MUL,
        2,
        "x",
        TokenType.MUL,
        3,
        "y",
        12,
        TokenType.EQ,
        "x",
        4,
    )

    with pytest.raises(ValueError):
        parser.eval("[x=3, x=3]")

    with pytest.raises(ValueError):
        parser.eval("[x>3, y=5]")

    with pytest.raises(SyntaxError):
        parser.eval("[x=3,]")
