from datatypes import Number, Product, Term
from processing import AST


def test_simplify_constants():
    assert AST("10 + 5 - 3").eval() == Term(Number(12))
    assert AST("20 - 4 + 2").eval() == Term(Number(18))
    assert AST("2 * 3 + 4").eval() == Term(Number(10))
    assert AST("10 / 2 + 5").eval() == Term(Number(10))
    assert AST("2^3 + 1").eval() == Term(Number(9))
    assert AST("(2 + 3) * 4").eval() == Term(Number(20))
    assert AST("10 / (2 + 3)").eval() == Term(Number(2))
    assert AST("2 * (3 + 4)").eval() == Term(Number(14))
    assert AST("(2 + 3) * (4 + 1)").eval() == Term(Number(25))


def test_merge_complex():
    assert AST("(3+4i) + (1+2i)").eval() == Term(Number(complex(4, 6)))
    assert AST("5 + 3i").eval() == Term(Number(complex(5, 3)))
    assert AST("(6+2i) + (-6+6i)").eval() == Term(Number(complex(0, 8)))
    assert AST("(6+5i) - (4+3i)").eval() == Term(Number(complex(2, 2)))
    assert AST("(3+7i) - (3+7i)").eval() == Term(Number())
    assert AST("(12+3i) - (12-1i)").eval() == Term(Number(complex(0, 4)))


def test_multiply_complex():
    assert AST("i*i").eval() == Term(Number(-1))
    assert AST("(2+3i)(1+4i)").eval() == Term(Number(complex(-10, 11)))
    assert AST("3(4-5i)").eval() == Term(Number(complex(12, -15)))
    assert AST("(-2+3i)(-1-4i)").eval() == Term(Number(complex(14, 5)))


def test_divide_complex():
    assert AST("(4+6i)/2").eval() == Term(Number(complex(2, 3)))
    assert AST("(8-4i)/-2").eval() == Term(Number(complex(-4, 2)))
    assert AST("(4+2i)/(1-i)").eval() == Term(Number(complex(1, 3)))
    assert AST("(6+3i)/(-2+i)").eval() == Term(Number(complex(-9, -12), 5))
    assert AST("(-2+i)/(2+3i)").eval() == Term(Number(complex(-1, 8), 13))
    assert AST("(3+4i)/(1-2i)").eval() == Term(Number(complex(-1, 2)))
    assert AST("0/(1+i)").eval() == Term(Number())


def test_numeric_exponentiation():
    # Exponentiation
    assert AST("5 ^ 2").eval() == Term(Number(25))
    assert AST("-3 ^ 2").eval() == Term(Number(-9))
    assert AST("(-3) ^ 2").eval() == Term(Number(9))
    assert AST("2 ^- 1").eval() == Term(Number(1, 2))

    # Perfect Radicals
    assert AST("2 √ 25").eval() == Term(Number(5))
    assert AST("2 √ 25").eval() == Term(Number(5))
    assert AST("2 √ -1").eval() == Term(Number(complex(imag=1)))
    assert AST("2 √ -81").eval() == Term(Number(complex(imag=9)))
    assert AST("3 √ 27").eval() == Term(Number(3))
    assert AST("3 √ -27").eval() == Term(Number(-3))

    # Imperfect radicals
    assert AST("2 √ 50").eval() == Term(Number(5), Number(2), Number(1, 2))
    assert AST("2 √ 192").eval() == Term(Number(8), Number(3), Number(1, 2))
    assert AST("3 √ 81").eval() == Term(Number(3), Number(3), Number(1, 3))
    assert AST("2 √ 27").eval() == Term(Number(3), Number(3), exp=Number(1, 2))
    assert AST("6 √ 27").eval() == Term(value=Number(3), exp=Number(1, 2))
    assert AST("4 √ -16").eval() == Term(Number(complex(imag=2)))
    assert AST("2 √ -128").eval() == Term(
        Number(complex(imag=8)), Number(2), Number(1, 2)
    )


def test_cancels_radical():
    # Simplify canceling radicals with like exponents
    assert AST("(2 √ -50)^2").eval() == Term(Number(-50))
    assert AST("(3 √ -81)^3").eval() == Term(Number(-81))
    assert AST("(2√5) * (2√5)").eval() == Term(Number(5))
    assert AST("(2√-5) * (2√5)").eval() == Term(Number(complex(imag=5)))
    assert AST("(2√32) * (2√2)").eval() == Term(Number(8))
    assert AST("(3√9) * (3√3)").eval() == Term(Number(3))

    # Simplify canceling radicals with like bases
    assert AST("27^(1/2) * 27^(-1/6)").eval() == Term(Number(3))
    assert AST("8^(1/2) * 8^(1/3)").eval() == Term(Number(4), Number(2), Number(1, 2))
    assert AST("2(2√2) * 3√8").eval() == Term(Number(4), Number(2), Number(1, 2))
    assert AST("4(2√2) * 2√8").eval() == Term(Number(16))


def test_multiply_radicals():
    assert AST("(2√27)(2√2)(1/(6√27))").eval() == Term(
        Number(3), Number(2), Number(1, 2)
    )
    assert AST("(2√8)(2√2)(1/(4√16))").eval() == Term(Number(2))
    assert AST("(2√50)(2√2)(1/(5√100))").eval() == Term(
        value=Number(1000), exp=Number(1, 5)
    )
    assert AST("(2√18)(2√2)(1/(3√9))").eval() == Term(
        Number(2), Number(3), Number(1, 3)
    )
    # NOTE: Writing it as 2(2√6)3(2√2)(1/(3√12)) will fail. Needs fix
    # The product class simplification should be aware of radical numbers
    assert AST("2(2√6) * 3(2√2) * (1/(3√12))").eval() == Term(
        Number(2),
        Product(
            [
                Term(value=Number(3), exp=Number(1, 2)),
                Term(value=Number(18), exp=Number(1, 3)),
            ]
        ),
    )
