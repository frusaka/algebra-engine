import pytest
from processing import AST, Token, TokenType, Binary, Unary
from datatypes import Variable, Number


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
    assert AST("-2") == Unary("NEG", Number(2))
    assert AST("-f") == Unary("NEG", Variable("f"))
    assert AST("+5") == Unary("POS", Number(5))
    assert AST("+x") == Unary("POS", Variable("x"))
    assert AST("--f") == Unary("NEG", Unary("NEG", Variable("f")))


def test_binary():
    assert AST("2*3") == Binary("MUL", Number(2), Number(3))
    assert AST("2/3") == Binary("TRUEDIV", Number(2), Number(3))
    assert AST("x+3") == Binary("ADD", Variable("x"), Number(3))
    assert AST("x+z") == Binary("ADD", Variable("x"), Variable("z"))
    assert AST("x=3") == Binary("EQ", Variable("x"), Number(3))
    assert AST("x>=3") == Binary("GE", Variable("x"), Number(3))
    assert AST("x<=3") == Binary("LE", Variable("x"), Number(3))
    assert AST("x>3") == Binary("GT", Variable("x"), Number(3))
    assert AST("x<3") == Binary("LT", Variable("x"), Number(3))


def test_unary_vs_binary():
    assert AST("3+-5") == Binary(
        "ADD",
        Number(3),
        Unary("NEG", Number(5)),
    )
    assert AST("-5+3") == Binary(
        "ADD",
        Unary("NEG", Number(5)),
        Number(3),
    )
    assert AST("3++5") == Binary(
        "ADD",
        Number(3),
        Unary("POS", Number(5)),
    )
    assert AST("3+++5") == Binary(
        "ADD",
        Number(3),
        Unary("POS", Unary("POS", Number(5))),
    )
    assert AST("3--5") == Binary(
        "SUB",
        Number(3),
        Unary("NEG", Number(5)),
    )
    assert AST("3---5") == Binary(
        "SUB",
        Number(3),
        Unary("NEG", Unary("NEG", Number(5))),
    )


def test_PEMDAS():
    # Basic operations
    assert AST("3+5*2") == Binary(
        "ADD",
        Number(3),
        Binary("MUL", Number(5), Number(2)),
    )
    assert AST("3-5/2") == Binary(
        "SUB",
        Number(3),
        Binary("TRUEDIV", Number(5), Number(2)),
    )
    assert AST("3/5*2") == Binary(
        "MUL",
        Binary("TRUEDIV", Number(3), Number(5)),
        Number(2),
    )
    assert AST("3*5/2") == Binary(
        "TRUEDIV",
        Binary("MUL", Number(3), Number(5)),
        Number(2),
    )

    # Exponentiation
    assert AST("3^5*2") == Binary(
        "MUL",
        Binary("POW", Number(3), Number(5)),
        Number(2),
    )
    assert AST("-3^5") == Unary(
        "NEG",
        Binary("POW", Number(3), Number(5)),
    )
    assert AST("(-3)^5") == Binary(
        "POW",
        Unary("NEG", Number(3)),
        Number(5),
    )
    assert AST("3^-5") == Binary(
        "POW",
        Number(3),
        Unary("NEG", Number(5)),
    )

    # Parentheses
    assert AST("(3+5)*2") == Binary(
        "MUL",
        Binary("ADD", Number(3), Number(5)),
        Number(2),
    )
    assert AST("3*(5+2)-8/4") == Binary(
        "SUB",
        Binary(
            "MUL",
            Number(3),
            Binary("ADD", Number(5), Number(2)),
        ),
        Binary("TRUEDIV", Number(8), Number(4)),
    )
    assert AST("3+(5*2-8)/4") == Binary(
        "ADD",
        Number(3),
        Binary(
            "TRUEDIV",
            Binary(
                "SUB",
                Binary("MUL", Number(5), Number(2)),
                Number(8),
            ),
            Number(4),
        ),
    )

    # Variables and coefficients
    assert AST("3x+5*2") == Binary(
        "ADD",
        Binary("MUL", Number(3), Variable("x")),
        Binary("MUL", Number(5), Number(2)),
    )
    assert AST("3(x+5)*2") == Binary(
        "MUL",
        Binary(
            "MUL",
            Number(3),
            Binary("ADD", Variable("x"), Number(5)),
        ),
        Number(2),
    )
    assert AST("2x^2 + 3x + 1") == Binary(
        "ADD",
        Binary(
            "ADD",
            Binary(
                "MUL",
                Number(2),
                Binary("POW", Variable("x"), Number(2)),
            ),
            Binary("MUL", Number(3), Variable("x")),
        ),
        Number(1),
    )

    # Comparisons and Comparisons
    assert AST("3+5=x") == Binary(
        "EQ",
        Binary("ADD", Number(3), Number(5)),
        Variable("x"),
    )
    assert AST("3=x+5") == Binary(
        "EQ",
        Number(3),
        Binary("ADD", Variable("x"), Number(5)),
    )
    assert AST("3+5=x") == Binary(
        "EQ",
        Binary("ADD", Number(3), Number(5)),
        Variable("x"),
    )
    assert AST("3<=x+5") == Binary(
        "LE",
        Number(3),
        Binary("ADD", Variable("x"), Number(5)),
    )


def test_monomial_special():
    assert AST("6a/8b") == Binary(
        "TRUEDIV",
        Binary("MUL", Number(6), Variable("a")),
        Binary("MUL", Number(8), Variable("b")),
    )
    assert AST("6/8b") == Binary(
        "TRUEDIV",
        Number(6),
        Binary("MUL", Number(8), Variable("b")),
    )
    assert AST("6/8*b") == Binary(
        "MUL",
        Binary("TRUEDIV", Number(6), Number(8)),
        Variable("b"),
    )
    assert AST("6a/8") == Binary(
        "TRUEDIV",
        Binary("MUL", Number(6), Variable("a")),
        Number(8),
    )
    assert AST("6a/8b^2") == Binary(
        "TRUEDIV",
        Binary("MUL", Number(6), Variable("a")),
        Binary(
            "MUL",
            Number(8),
            Binary("POW", Variable("b"), Number(2)),
        ),
    )
