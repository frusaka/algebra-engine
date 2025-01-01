from string import ascii_letters
from processing import Lexer, Token, TokenType
from data_types import Number, Variable


def test_number():
    assert list(Lexer("0").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(0))
    ]
    assert list(Lexer("3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3))
    ]
    assert list(Lexer("0013").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(13))
    ]
    assert list(Lexer("12").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(12))
    ]
    assert list(Lexer("12.13").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(1213, 100))
    ]
    assert list(Lexer(".14").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(14, 100))
    ]
    assert list(Lexer("123.").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(123))
    ]


def test_variable():
    for i in ascii_letters:
        assert list(Lexer(i).generate_tokens())[1:-1] == [
            Token(TokenType.VAR, Variable(i))
        ]


def test_binary():
    assert list(Lexer("2+3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(3)),
    ]
    assert list(Lexer("2-3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.SUB),
        Token(TokenType.NUMBER, Number(3)),
    ]
    assert list(Lexer("2*3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(3)),
    ]
    assert list(Lexer("2/3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.NUMBER, Number(3)),
    ]
    assert list(Lexer("2^3").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.POW),
        Token(TokenType.NUMBER, Number(3)),
    ]


def test_unary():
    assert list(Lexer("-5").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]

    assert list(Lexer("+5").generate_tokens())[1:-1] == [
        Token(TokenType.POS),
        Token(TokenType.NUMBER, Number(5)),
    ]


def test_unary_binary():
    assert list(Lexer("3+-5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("-5+3").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(3)),
    ]
    assert list(Lexer("3++5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("3+++5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.POS),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("3--5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("3---5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]


def test_ignore_space():
    assert list(Lexer("3 + -5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("   3  +-5").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("3+-5  ").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("- 5").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.NUMBER, Number(5)),
    ]


def test_multiple_operators():
    assert list(Lexer("3+5+2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3-5-2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.SUB),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.SUB),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3/5/2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3+5^2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.POW),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3*5+2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(2)),
    ]
