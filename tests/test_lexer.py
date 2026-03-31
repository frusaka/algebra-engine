import pytest
from parsing import Lexer, Token, TokenType
from datatypes.nodes import Const, Var


def test_unknown():
    assert list(Lexer("#").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("?").tokenize())[0].type is TokenType.ERROR
    # assert list(Lexer("$").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("@").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("!").tokenize())[0].type is TokenType.ERROR


def test_number():
    assert list(Lexer(".").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("0.1.1").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("..").tokenize())[0].type is TokenType.ERROR
    assert list(Lexer("0").tokenize()) == [Token(TokenType.CONST, Const(0))]
    assert list(Lexer("3").tokenize()) == [Token(TokenType.CONST, Const(3))]
    assert list(Lexer("0013").tokenize()) == [Token(TokenType.CONST, Const(13))]
    assert list(Lexer("12").tokenize()) == [Token(TokenType.CONST, Const(12))]
    assert list(Lexer("12.13").tokenize()) == [Token(TokenType.CONST, Const(1213, 100))]
    assert list(Lexer(".14").tokenize()) == [Token(TokenType.CONST, Const(14, 100))]
    assert list(Lexer("123.").tokenize()) == [Token(TokenType.CONST, Const(123))]


def test_variable():
    assert list(Lexer("x").tokenize()) == [Token(TokenType.VAR, Var("x"))]
    assert list(Lexer("b").tokenize()) == [Token(TokenType.VAR, Var("b"))]
    assert list(Lexer("H").tokenize()) == [Token(TokenType.VAR, Var("H"))]
    assert list(Lexer("J").tokenize()) == [Token(TokenType.VAR, Var("J"))]
    assert list(Lexer("J").tokenize()) != [Token(TokenType.VAR, Var("j"))]


def test_function():
    assert list(Lexer("sqrt").tokenize()) == [Token(TokenType.SQRT)]
    assert list(Lexer("subs").tokenize()) == [Token(TokenType.SUBS)]
    assert list(Lexer("factor").tokenize()) == [Token(TokenType.FACTOR)]
    assert list(Lexer("approx").tokenize()) == [Token(TokenType.APPROX)]
    assert list(Lexer("lcm").tokenize()) == [Token(TokenType.LCM)]
    assert list(Lexer("gcd").tokenize()) == [Token(TokenType.GCD)]

    # latex functions
    assert list(Lexer("\\sqrt").tokenize()) == [Token(TokenType.SQRT)]
    assert list(Lexer("\\sqrt 4").tokenize()) == [
        Token(TokenType.SQRT),
        Token(TokenType.LPAREN),
        Token(TokenType.NaN),
        Token(TokenType.COMMA),
        Token(TokenType.CONST, Const(4)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("\\solve").tokenize()) == [Token(TokenType.SOLVE)]
    assert list(Lexer("\\factor").tokenize()) == [Token(TokenType.FACTOR)]
    assert list(Lexer("\\expand").tokenize()) == [Token(TokenType.EXPAND)]
    assert list(Lexer("\\subs").tokenize()) == [Token(TokenType.SUBS)]
    assert list(Lexer("\\approx").tokenize()) == [Token(TokenType.APPROX)]
    assert list(Lexer("\\lcm").tokenize()) == [Token(TokenType.LCM)]
    assert list(Lexer("\\gcd").tokenize()) == [Token(TokenType.GCD)]
    assert list(Lexer("\\solve{x=5}").tokenize()) == [
        Token(TokenType.SOLVE),
        Token(TokenType.LPAREN),
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.EQ),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.RPAREN),
    ]


def test_parentheses():
    assert list(Lexer("(3)").tokenize()) == [
        Token(TokenType.LPAREN),
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("(()").tokenize()) == [
        Token(TokenType.LPAREN),
        Token(TokenType.LPAREN),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("\\left(\\right)").tokenize()) == [
        Token(TokenType.LPAREN),
        Token(TokenType.RPAREN),
    ]

    assert list(Lexer("[]").tokenize()) == [
        Token(TokenType.LBRACK),
        Token(TokenType.RBRACK),
    ]
    assert list(Lexer("[[").tokenize()) == [
        Token(TokenType.LBRACK),
        Token(TokenType.LBRACK),
    ]
    assert list(Lexer("[]]").tokenize()) == [
        Token(TokenType.LBRACK),
        Token(TokenType.RBRACK),
        Token(TokenType.RBRACK),
    ]

    assert list(Lexer("\\left[\\right]").tokenize()) == [
        Token(TokenType.LBRACK),
        Token(TokenType.RBRACK),
    ]
    assert list(Lexer("\\left\\lbrack\\right\\rbrack").tokenize()) == [
        Token(TokenType.LBRACK),
        Token(TokenType.RBRACK),
    ]


def test_binary():
    assert list(Lexer("2+3").tokenize()) == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2-3").tokenize()) == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2*3").tokenize()) == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2/3").tokenize()) == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.DIV),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("2^3").tokenize()) == [
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.POW),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("x=5").tokenize()) == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.EQ),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x>=5").tokenize()) == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.GE),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x<=5").tokenize()) == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.LE),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x>5").tokenize()) == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.GT),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("x<5").tokenize()) == [
        Token(TokenType.VAR, Var("x")),
        Token(TokenType.LT),
        Token(TokenType.CONST, Const(5)),
    ]
    # Latex operators
    assert list(Lexer("\\frac34").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.DIV),
        Token(TokenType.CONST, Const(4)),
    ]
    assert list(Lexer("3\\cdot4").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(4)),
    ]
    assert list(Lexer("3\\times4").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(4)),
    ]
    assert list(Lexer("3\\div4").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.DIV),
        Token(TokenType.CONST, Const(4)),
    ]


def test_unary():
    assert list(Lexer("-5").tokenize()) == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]

    assert list(Lexer("+5").tokenize()) == [
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]


def test_unary_vs_binary():
    assert list(Lexer("3+-5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("-5+3").tokenize()) == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(3)),
    ]
    assert list(Lexer("3++5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3+++5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.POS),
        Token(TokenType.POS),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3--5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3---5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.NEG),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]


def test_ignore_spaces():
    assert list(Lexer("3 + -5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("   3  +-5").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("3+-5  ").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]
    assert list(Lexer("- 5").tokenize()) == [
        Token(TokenType.NEG),
        Token(TokenType.CONST, Const(5)),
    ]


def test_multiple_operators():
    assert list(Lexer("3+5+2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3-5-2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.SUB),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3/5/2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.DIV),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.DIV),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3+5^2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.POW),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5+2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
    ]
    # Comparison operators
    assert list(Lexer("3*5=2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.EQ),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5>=2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.GE),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5<=2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.LE),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5<2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.LT),
        Token(TokenType.CONST, Const(2)),
    ]
    assert list(Lexer("3*5>2").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(5)),
        Token(TokenType.GT),
        Token(TokenType.CONST, Const(2)),
    ]


def test_alt_syntax():
    assert list(Lexer("3(4)").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL),
        Token(TokenType.LPAREN),
        Token(TokenType.CONST, Const(4)),
        Token(TokenType.RPAREN),
    ]
    assert list(Lexer("3y").tokenize()) == [
        Token(TokenType.CONST, Const(3)),
        Token(TokenType.MUL, iscoef=True),
        Token(TokenType.VAR, Var("y")),
    ]
    assert list(Lexer("(y+2)3").tokenize()) == [
        Token(TokenType.LPAREN),
        Token(TokenType.VAR, Var("y")),
        Token(TokenType.ADD),
        Token(TokenType.CONST, Const(2)),
        Token(TokenType.RPAREN),
        Token(TokenType.MUL),
        Token(TokenType.CONST, Const(3)),
    ]
