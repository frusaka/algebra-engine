from datatypes.nodes import Const
from utils import simplify_radical
from parsing import parser


def test_simplify_constants():
    assert parser.eval("10 + 5 - 3") == Const(12)
    assert parser.eval("20 - 4 + 2") == Const(18)
    assert parser.eval("2 * 3 + 4") == 10
    assert parser.eval("10 / 2 + 5") == 10
    assert parser.eval("2^3 + 1") == Const(9)
    assert parser.eval("(2 + 3) * 4") == 20
    assert parser.eval("10 / (2 + 3)") == 2
    assert parser.eval("2 * (3 + 4)") == 14
    assert parser.eval("(2 + 3) * (4 + 1)") == Const(25)


def test_merge_complex():
    assert parser.eval("(3+4i) + (1+2i)") == (Const(complex(4, 6)))
    assert parser.eval("5 + 3i") == (Const(complex(5, 3)))
    assert parser.eval("(6+2i) + (-6+6i)") == (Const(complex(0, 8)))
    assert parser.eval("(6+5i) - (4+3i)") == (Const(complex(2, 2)))
    assert parser.eval("(3+7i) - (3+7i)") == (Const())
    assert parser.eval("(12+3i) - (12-1i)") == (Const(complex(0, 4)))


def test_multiply_complex():
    assert parser.eval("i*i") == (Const(-1))
    assert parser.eval("(2+3i)(1+4i)") == (Const(complex(-10, 11)))
    assert parser.eval("3(4-5i)") == (Const(complex(12, -15)))
    assert parser.eval("(-2+3i)(-1-4i)") == (Const(complex(14, 5)))


def test_divide_complex():
    assert parser.eval("(4+6i)/2") == Const(2 + 3j)
    assert parser.eval("(8-4i)/-2") == Const(-4 + 2j)
    assert parser.eval("(4+2i)/(1-i)") == Const(1 + 3j)
    assert parser.eval("(6+3i)/(-2+i)") == Const(-9 - 12j, 5)
    assert parser.eval("(-2+i)/(2+3i)") == Const(-1 + 8j, 13)
    assert parser.eval("(3+4i)/(1-2i)") == Const(-1 + 2j)
    assert parser.eval("0/(1+i)") == 0


def test_numeric_exponentiation():
    # Exponentiation
    assert parser.eval("5 ^ 2") == 25
    assert parser.eval("-3 ^ 2") == -9
    assert parser.eval("(-3) ^ 2") == 9
    assert parser.eval("2 ^- 1") == Const(1, 2)

    # Perfect Radicals
    assert parser.eval("25^0.5") == 5
    assert parser.eval("(-1)^0.5") == Const(1j)
    assert parser.eval("(-81)^0.5") == Const(9j)
    assert parser.eval("27^(1/3)") == Const(3)
    assert parser.eval("(-27)^(1/3)") == Const(-3)

    # Imperfect radicals
    # Format = Constant, base, power
    assert simplify_radical(50, 2) == (5, 2, Const(1, 2))
    assert simplify_radical(192, 2) == (8, 3, Const(1, 2))
    assert simplify_radical(81, 3) == (3, 3, Const(1, 3))
    assert simplify_radical(27, 2) == (3, 3, Const(1, 2))
    assert simplify_radical(27, 6) == (1, 3, Const(1, 2))
    assert simplify_radical(-128, 2) == (Const(8j), 2, Const(1, 2))
    # Edge cases: even radicals greater than 2
    assert simplify_radical(-1, 4) == (1, -1, Const(1, 4))
    assert simplify_radical(-16, 4) == (2, -1, Const(1, 4))
    assert simplify_radical(-27, 6) == (1, -27, Const(1, 6))


def test_multiply_radicals():
    assert parser.eval("((-50)^0.5)^2") == -50

    assert parser.eval("8^(1/2) * 8^(1/3)") == 4 * Const(2) ** Const(1, 2)
    assert parser.eval("4(2^0.5) * 8^0.5") == Const(16)
    assert parser.eval("(-5)^0.5 * (5)^0.5") == (Const(5j))

    assert parser.eval("27^0.5(1/27^(1/6))2^0.5") == Const(3) * Const(2) ** Const(1, 2)
    assert parser.eval("(1/(16^0.25))8^0.5*2^0.5") == Const(2)
    assert parser.eval("50^0.5(1/100^.2)2^0.5") == Const(1000) ** Const(1, 5)
    assert parser.eval("18^0.5*2^0.5(1/9^(1/3))") == 2 * 3 ** Const(1, 3)
    assert parser.eval("2(6^0.5) * 3(2^0.5) * (1/(12^(1/3)))") == (
        6 * 12 ** Const(1, 6)
    )
