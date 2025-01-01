import pytest
from processing import AST, Token, TokenType, Binary, Unary
from data_types import Variable, Number


@pytest.mark.parametrize("expr", ["9+", "-4+", "3()", "(()", ")", "()^2"])
def test_invalid(expr):
    with pytest.raises(SyntaxError):
        AST(expr)


@pytest.mark.skip(reason="Case not in check")
def test_spaced_numbers():
    with pytest.raises(SyntaxError):
        AST("12 0.4")


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
    assert AST("(3+5)*2") == Binary(
        Token(TokenType.MUL),
        Binary(Token(TokenType.ADD), Number(3), Number(5)),
        Number(2),
    )

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
