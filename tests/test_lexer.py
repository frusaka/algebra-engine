import pytest
from parsing import Lexer, Token, TokenType
from datatypes.nodes import Const, Var


def test_unknown():
    assert list(Lexer("#").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("?").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("$").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("@").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("!").generate_tokens())[1].type is TokenType.ERROR


def test_number():
    assert list(Lexer(".").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("0.1.1").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("..").generate_tokens())[1].type is TokenType.ERROR
    assert list(Lexer("0").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(0))
    ]
    assert list(Lexer("3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3))
    ]
    assert list(Lexer("0013").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(13))
    ]
    assert list(Lexer("12").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(12))
    ]
    assert list(Lexer("12.13").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(1213, 100))
    ]
    assert list(Lexer(".14").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(14, 100))
    ]
    assert list(Lexer("123.").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(123))
    ]


def test_variable():
    assert list(Lexer("x").generate_tokens())[1:-1] == [Token(TokenType.VAR, Var("x"))]
    assert list(Lexer("b").generate_tokens())[1:-1] == [Token(TokenType.VAR, Var("b"))]
    assert list(Lexer("H").generate_tokens())[1:-1] == [Token(TokenType.VAR, Var("H"))]
    assert list(Lexer("J").generate_tokens())[1:-1] == [Token(TokenType.VAR, Var("J"))]
    assert list(Lexer("J").generate_tokens())[1:-1] != [Token(TokenType.VAR, Var("j"))]


def test_parentheses():
    assert list(Lexer("(3)").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("(()").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.LPAREN),
        Token(TokenType.RPAREN),
    ]


def test_binary():
    assert list(Lexer("2+3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2-3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2*3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2/3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2^3").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.POW),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("x=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.EQ),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x>=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.GE),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x<=5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.LE),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x>5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.GT),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x<5").generate_tokens())[1:-1] == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.LT),
        Token(TokenType.CONST, Const(5)),
    ]


def test_unary():
    assert list(Lexer("-5").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]

    assert list(Lexer("+5").generate_tokens())[1:-1] == [
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]


def test_unary_vs_binary():
    assert list(Lexer("3+-5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("-5+3").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("3++5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3+++5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3--5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3---5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]


def test_ignore_spaces():
    assert list(Lexer("3 + -5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("   3  +-5").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3+-5  ").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("- 5").generate_tokens())[1:-1] == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]


def test_multiple_operators():
    assert list(Lexer("3+5+2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3-5-2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3/5/2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.TRUEDIV),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3+5^2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.POW),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5+2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
    ]
    # Comparison operators
    assert list(Lexer("3*5=2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.EQ),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5>=2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.GE),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5<=2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.LE),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5<2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.LT),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5>2").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.GT),
        Token(TokenType.CONST, Const(2)),
    ]


def test_alt_syntax():
    assert list(Lexer("3(4)").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL, iscoef=True),
        Token(TokenType.LPAREN),
        Token(TokenType.CONST, Const(4)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("3y").generate_tokens())[1:-1] == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL, iscoef=True),
        Token(TokenType.VAR, Var("y")),
    ]
    assert list(Lexer("(y+2)3").generate_tokens())[1:-1] == [
        Token(TokenType.LPAREN),
        Token(TokenType.VAR, Var("y")),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.RPAREN),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(3)),
    ]
