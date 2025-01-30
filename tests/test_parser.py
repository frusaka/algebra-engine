import pytest
from processing import AST, Token, TokenType, Binary, Unary
from data_types import Variable, Number


@pytest.mark.parametrize("expr", ["9+", "-4+", "3()", "(()", ")", "()^2"])
def test_invalid(expr):
    with pytest.raises(SyntaxError):
        AST(expr)


@pytest.mark.parametrize("expr", ["3 4", "2 3y", "3 4+5", "3/4 5x"])
def test_spaced_numbers(expr):
    with pytest.raises(SyntaxError):
        AST(expr)


def test_unary():
    assert AST("-2") == Unary(Token(TokenType.NEG), Number(2))
    assert AST("-f") == Unary(Token(TokenType.NEG), Variable("f"))
    assert AST("+5") == Unary(Token(TokenType.POS), Number(5))
    assert AST("+x") == Unary(Token(TokenType.POS), Variable("x"))
    assert AST("--f") == Unary(
        Token(TokenType.NEG), Unary(Token(TokenType.NEG), Variable("f"))
    )


def test_binary():
    assert AST("2*3") == Binary(Token(TokenType.MUL), Number(2), Number(3))
    assert AST("2/3") == Binary(Token(TokenType.TRUEDIV), Number(2), Number(3))
    assert AST("x+3") == Binary(Token(TokenType.ADD), Variable("x"), Number(3))
    assert AST("x+z") == Binary(Token(TokenType.ADD), Variable("x"), Variable("z"))
    assert AST("x=3") == Binary(Token(TokenType.EQ), Variable("x"), Number(3))
    assert AST("x>=3") == Binary(Token(TokenType.GE), Variable("x"), Number(3))
    assert AST("x<=3") == Binary(Token(TokenType.LE), Variable("x"), Number(3))
    assert AST("x>3") == Binary(Token(TokenType.GT), Variable("x"), Number(3))
    assert AST("x<3") == Binary(Token(TokenType.LT), Variable("x"), Number(3))


def test_unary_vs_binary():
    assert AST("3+-5") == Binary(
        Token(TokenType.ADD),
        Number(3),
        Unary(Token(TokenType.NEG), Number(5)),
    )
    assert AST("-5+3") == Binary(
        Token(TokenType.ADD),
        Unary(Token(TokenType.NEG), Number(5)),
        Number(3),
    )
    assert AST("3++5") == Binary(
        Token(TokenType.ADD),
        Number(3),
        Unary(Token(TokenType.POS), Number(5)),
    )
    assert AST("3+++5") == Binary(
        Token(TokenType.ADD),
        Number(3),
        Unary(Token(TokenType.POS), Unary(Token(TokenType.POS), Number(5))),
    )
    assert AST("3--5") == Binary(
        Token(TokenType.SUB),
        Number(3),
        Unary(Token(TokenType.NEG), Number(5)),
    )
    assert AST("3---5") == Binary(
        Token(TokenType.SUB),
        Number(3),
        Unary(Token(TokenType.NEG), Unary(Token(TokenType.NEG), Number(5))),
    )


def test_PEMDAS():
    # Basic operations
    assert AST("3+5*2") == Binary(
        Token(TokenType.ADD),
        Number(3),
        Binary(Token(TokenType.MUL), Number(5), Number(2)),
    )
    assert AST("3-5/2") == Binary(
        Token(TokenType.SUB),
        Number(3),
        Binary(Token(TokenType.TRUEDIV), Number(5), Number(2)),
    )
    assert AST("3/5*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.TRUEDIV), Number(3), Number(5)),
        Number(2),
    )
    assert AST("3*5/2") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL), Number(3), Number(5)),
        Number(2),
    )

    # Exponentiation
    assert AST("3^5*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.POW), Number(3), Number(5)),
        Number(2),
    )
    assert AST("-3^5") == Unary(
        Token(TokenType.NEG),
        Binary(Token(TokenType.POW), Number(3), Number(5)),
    )
    assert AST("(-3)^5") == Binary(
        Token(TokenType.POW),
        Unary(Token(TokenType.NEG), Number(3)),
        Number(5),
    )
    assert AST("3^-5") == Binary(
        Token(TokenType.POW),
        Number(3),
        Unary(Token(TokenType.NEG), Number(5)),
    )

    # Parentheses
    assert AST("(3+5)*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.ADD), Number(3), Number(5)),
        Number(2),
    )
    assert AST("3*(5+2)-8/4") == Binary(
        Token(TokenType.SUB),
        Binary(
            Token(TokenType.MUL),
            Number(3),
            Binary(Token(TokenType.ADD), Number(5), Number(2)),
        ),
        Binary(Token(TokenType.TRUEDIV), Number(8), Number(4)),
    )
    assert AST("3+(5*2-8)/4") == Binary(
        Token(TokenType.ADD),
        Number(3),
        Binary(
            Token(TokenType.TRUEDIV),
            Binary(
                Token(TokenType.SUB),
                Binary(Token(TokenType.MUL), Number(5), Number(2)),
                Number(8),
            ),
            Number(4),
        ),
    )

    # Variables and coefficients
    assert AST("3x+5*2") == Binary(
        Token(TokenType.ADD),
        Binary(Token(TokenType.MUL, iscoef=True), Number(3), Variable("x")),
        Binary(Token(TokenType.MUL), Number(5), Number(2)),
    )
    assert AST("3(x+5)*2") == Binary(
        Token(TokenType.MUL),
        Binary(
            Token(TokenType.MUL, iscoef=True),
            Number(3),
            Binary(Token(TokenType.ADD), Variable("x"), Number(5)),
        ),
        Number(2),
    )
    assert AST("2x^2 + 3x + 1") == Binary(
        Token(TokenType.ADD),
        Binary(
            Token(TokenType.ADD),
            Binary(
                Token(TokenType.MUL, iscoef=True),
                Number(2),
                Binary(Token(TokenType.POW), Variable("x"), Number(2)),
            ),
            Binary(Token(TokenType.MUL, iscoef=True), Number(3), Variable("x")),
        ),
        Number(1),
    )

    # Comparisons and Comparisons
    assert AST("3+5=x") == Binary(
        Token(TokenType.EQ),
        Binary(Token(TokenType.ADD), Number(3), Number(5)),
        Variable("x"),
    )
    assert AST("3=x+5") == Binary(
        Token(TokenType.EQ),
        Number(3),
        Binary(Token(TokenType.ADD), Variable("x"), Number(5)),
    )
    assert AST("3+5=x") == Binary(
        Token(TokenType.EQ),
        Binary(Token(TokenType.ADD), Number(3), Number(5)),
        Variable("x"),
    )
    assert AST("3<=x+5") == Binary(
        Token(TokenType.LE),
        Number(3),
        Binary(Token(TokenType.ADD), Variable("x"), Number(5)),
    )


def test_monomial_special():
    assert AST("6a/8b") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Number(6), Variable("a")),
        Binary(Token(TokenType.MUL, iscoef=True), Number(8), Variable("b")),
    )
    assert AST("6/8b") == Binary(
        Token(TokenType.TRUEDIV),
        Number(6),
        Binary(Token(TokenType.MUL, iscoef=True), Number(8), Variable("b")),
    )
    assert AST("6/8*b") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.TRUEDIV), Number(6), Number(8)),
        Variable("b"),
    )
    assert AST("6a/8") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Number(6), Variable("a")),
        Number(8),
    )
    assert AST("6a/8b^2") == Binary(
        Token(TokenType.TRUEDIV),
        Binary(Token(TokenType.MUL, iscoef=True), Number(6), Variable("a")),
        Binary(
            Token(TokenType.MUL, iscoef=True),
            Number(8),
            Binary(Token(TokenType.POW), Variable("b"), Number(2)),
        ),
    )
