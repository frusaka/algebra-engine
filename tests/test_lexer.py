import pytest
from processing import Lexer, Token, TokenType
from data_types import Number, Variable


def test_unknown():
    assert list(Lexer("~").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("$").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("@").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("!").generate_tokens())[1].type is TokenType.ERROR


def test_number():
    assert list(Lexer(".").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("0.1.1").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("..").generate_tokens())[1].type is TokenType.ERROR
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
        Token(TokenType.NUMBER, Number("1213/100"))
    ]
    assert list(Lexer(".14").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number("14/100"))
    ]
    assert list(Lexer("123.").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(123))
    ]


def test_variable():
    assert list(Lexer("x").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x"))
    ]
    assert list(Lexer("b").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("b"))
    ]
    assert list(Lexer("H").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("H"))
    ]
    assert list(Lexer("J").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("J"))
    ]
    assert list(Lexer("J").generate_tokens())[1:-1] != [
        Token(TokenType.VAR, Variable("j"))
    ]


def test_parentheses():
    assert list(Lexer("(3)").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("(()").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.LPAREN),
        Token(TokenType.RPAREN),
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
    assert list(Lexer("x=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x")),
        Token(TokenType.EQ),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("x>=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x")),
        Token(TokenType.GE),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("x<=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x")),
        Token(TokenType.LE),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("x>5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x")),
        Token(TokenType.GT),
        Token(TokenType.NUMBER, Number(5)),
    ]
    assert list(Lexer("x<5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Variable("x")),
        Token(TokenType.LT),
        Token(TokenType.NUMBER, Number(5)),
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


def test_unary_vs_binary():
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


def test_ignore_spaces():
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
    # Comparison operators
    assert list(Lexer("3*5=2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.EQ),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3*5>=2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.GE),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3*5<=2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.LE),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3*5<2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.LT),
        Token(TokenType.NUMBER, Number(2)),
    ]
    assert list(Lexer("3*5>2").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(5)),
        Token(TokenType.GT),
        Token(TokenType.NUMBER, Number(2)),
    ]


def test_alt_syntax():
    assert list(Lexer("3(4)").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL, iscoef=True),
        Token(TokenType.LPAREN),
        Token(TokenType.NUMBER, Number(4)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("3y").generate_tokens())[1:-1] == [
        Token(TokenType.NUMBER, Number(3)),
        Token(TokenType.MUL, iscoef=True),
        Token(TokenType.VAR, Variable("y")),
    ]
    assert list(Lexer("(y+2)3").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.VAR, Variable("y")),
        Token(TokenType.ADD),
        Token(TokenType.NUMBER, Number(2)),
        Token(TokenType.RPAREN),
        Token(TokenType.MUL),
        Token(TokenType.NUMBER, Number(3)),
    ]
