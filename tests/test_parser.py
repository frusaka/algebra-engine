import pytest
from processing import parser, Token, TokenType
from datatypes.nodes import Var, Const


def test_invalid():
    # Uses for-loop to avoid inflating test count
    for expr in ["9+", "-4+", "3()", "(()", ")", "()^2", "()()", "j6"]:
        with pytest.raises(SyntaxError):
            AST(expr)


def test_spaced_numbers():
    for expr in ["3 4", "2 3y", "3 4+5", "3/4 5x"]:
        with pytest.raises(SyntaxError):
            AST(expr)


def test_unary():
    assert AST("-2") == Unary(Token(TokenType.NEG), Const(2))
    assert AST("-f") == Unary(Token(TokenType.NEG), Variable("f"))
    assert AST("+5") == Unary(Token(TokenType.POS), Const(5))
    assert AST("+x") == Unary(Token(TokenType.POS), Variable("x"))
    assert AST("--f") == Unary(
        Token(TokenType.NEG), Unary(Token(TokenType.NEG), Variable("f"))
    )


def test_binary():
    assert AST("2*3") == Binary(Token(TokenType.MUL), Const(2), Const(3))
    assert AST("2/3") == Binary(Token(TokenType.TRUEDIV), Const(2), Const(3))
    assert AST("x+3") == Binary(Token(TokenType.ADD), Variable("x"), Const(3))
    assert AST("x+z") == Binary(Token(TokenType.ADD), Variable("x"), Variable("z"))
    assert AST("x=3") == Binary(Token(TokenType.EQ), Variable("x"), Const(3))
    assert AST("x>=3") == Binary(Token(TokenType.GE), Variable("x"), Const(3))
    assert AST("x<=3") == Binary(Token(TokenType.LE), Variable("x"), Const(3))
    assert AST("x>3") == Binary(Token(TokenType.GT), Variable("x"), Const(3))
    assert AST("x<3") == Binary(Token(TokenType.LT), Variable("x"), Const(3))


def test_unary_vs_binary():
    assert AST("3+-5") == Binary(
        Token(TokenType.ADD),
        Const(3),
        Unary(Token(TokenType.NEG), Const(5)),
    )
    assert AST("-5+3") == Binary(
        Token(TokenType.ADD),
        Unary(Token(TokenType.NEG), Const(5)),
        Const(3),
    )
    assert AST("3++5") == Binary(
        Token(TokenType.ADD),
        Const(3),
        Unary(Token(TokenType.POS), Const(5)),
    )
    assert AST("3+++5") == Binary(
        Token(TokenType.ADD),
        Const(3),
        Unary(Token(TokenType.POS), Unary(Token(TokenType.POS), Const(5))),
    )
    assert AST("3--5") == Binary(
        Token(TokenType.SUB),
        Const(3),
        Unary(Token(TokenType.NEG), Const(5)),
    )
    assert AST("3---5") == Binary(
        Token(TokenType.SUB),
        Const(3),
        Unary(Token(TokenType.NEG), Unary(Token(TokenType.NEG), Const(5))),
    )


def test_PEMDAS():
    # Basic operations
    assert AST("3+5*2") == Binary(
        Token(TokenType.ADD),
        Const(3),
        Binary(Token(TokenType.MUL), Const(5), Const(2)),
    )
    assert AST("3-5/2") == Binary(
        Token(TokenType.SUB),
        Const(3),
        Binary(Token(TokenType.TRUEDIV), Const(5), Const(2)),
    )
    assert AST("3/5*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.TRUEDIV), Const(3), Const(5)),
        Const(2),
    )
    assert AST("3*5/2") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL), Const(3), Const(5)),
        Const(2),
    )

    # Exponentiation
    assert AST("3^5*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.POW), Const(3), Const(5)),
        Const(2),
    )
    assert AST("-3^5") == Unary(
        Token(TokenType.NEG),
        Binary(Token(TokenType.POW), Const(3), Const(5)),
    )
    assert AST("(-3)^5") == Binary(
        Token(TokenType.POW),
        Unary(Token(TokenType.NEG), Const(3)),
        Const(5),
    )
    assert AST("3^-5") == Binary(
        Token(TokenType.POW),
        Const(3),
        Unary(Token(TokenType.NEG), Const(5)),
    )

    # Parentheses
    assert AST("(3+5)*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.ADD), Const(3), Const(5)),
        Const(2),
    )
    assert AST("3*(5+2)-8/4") == Binary(
        Token(TokenType.SUB),
        Binary(
            Token(TokenType.MUL),
            Const(3),
            Binary(Token(TokenType.ADD), Const(5), Const(2)),
        ),
        Binary(Token(TokenType.TRUEDIV), Const(8), Const(4)),
    )
    assert AST("3+(5*2-8)/4") == Binary(
        Token(TokenType.ADD),
        Const(3),
        Binary(
            Token(TokenType.TRUEDIV),
            Binary(
                Token(TokenType.SUB),
                Binary(Token(TokenType.MUL), Const(5), Const(2)),
                Const(8),
            ),
            Const(4),
        ),
    )

    # Variables and coefficients
    assert AST("3x+5*2") == Binary(
        Token(TokenType.ADD),
        Binary(Token(TokenType.MUL, iscoef=True), Const(3), Variable("x")),
        Binary(Token(TokenType.MUL), Const(5), Const(2)),
    )
    assert AST("3(x+5)*2") == Binary(
        Token(TokenType.MUL),
        Binary(
            Token(TokenType.MUL, iscoef=True),
            Const(3),
            Binary(Token(TokenType.ADD), Variable("x"), Const(5)),
        ),
        Const(2),
    )
    assert AST("2x^2 + 3x + 1") == Binary(
        Token(TokenType.ADD),
        Binary(
            Token(TokenType.ADD),
            Binary(
                Token(TokenType.MUL, iscoef=True),
                Const(2),
                Binary(Token(TokenType.POW), Variable("x"), Const(2)),
            ),
            Binary(Token(TokenType.MUL, iscoef=True), Const(3), Variable("x")),
        ),
        Const(1),
    )

    # Comparisons and Comparisons
    assert AST("3+5=x") == Binary(
        Token(TokenType.EQ),
        Binary(Token(TokenType.ADD), Const(3), Const(5)),
        Variable("x"),
    )
    assert AST("3=x+5") == Binary(
        Token(TokenType.EQ),
        Const(3),
        Binary(Token(TokenType.ADD), Variable("x"), Const(5)),
    )
    assert AST("3+5=x") == Binary(
        Token(TokenType.EQ),
        Binary(Token(TokenType.ADD), Const(3), Const(5)),
        Variable("x"),
    )
    assert AST("3<=x+5") == Binary(
        Token(TokenType.LE),
        Const(3),
        Binary(Token(TokenType.ADD), Variable("x"), Const(5)),
    )


def test_monomial_special():
    assert AST("6a/8b") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Const(6), Variable("a")),
        Binary(Token(TokenType.MUL, iscoef=True), Const(8), Variable("b")),
    )
    assert AST("6/8b") == Binary(
        Token(TokenType.TRUEDIV),
        Const(6),
        Binary(Token(TokenType.MUL, iscoef=True), Const(8), Variable("b")),
    )
    assert AST("6/8*b") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.TRUEDIV), Const(6), Const(8)),
        Variable("b"),
    )
    assert AST("6a/8") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Const(6), Variable("a")),
        Const(8),
    )
    assert AST("6a/8b^2") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Const(6), Variable("a")),
        Binary(
            Token(TokenType.MUL, iscoef=True),
            Const(8),
            Binary(Token(TokenType.POW), Variable("b"), Const(2)),
        ),
    )
