from data_types import Number, Product, Term


def test_simplify_constants(processor, AST):
    assert processor.eval(AST("10 + 5 - 3")) == Term(Number(12))
    assert processor.eval(AST("20 - 4 + 2")) == Term(Number(18))
    assert processor.eval(AST("2 * 3 + 4")) == Term(Number(10))
    assert processor.eval(AST("10 / 2 + 5")) == Term(Number(10))
    assert processor.eval(AST("2^3 + 1")) == Term(Number(9))
    assert processor.eval(AST("(2 + 3) * 4")) == Term(Number(20))
    assert processor.eval(AST("10 / (2 + 3)")) == Term(Number(2))
    assert processor.eval(AST("2 * (3 + 4)")) == Term(Number(14))
    assert processor.eval(AST("(2 + 3) * (4 + 1)")) == Term(Number(25))


def test_merge_complex(processor, AST):
    assert processor.eval(AST("(3+4i) + (1+2i)")) == Term(Number(complex(4, 6)))
    assert processor.eval(AST("5 + 3i")) == Term(Number(complex(5, 3)))
    assert processor.eval(AST("(6+2i) + (-6+6i)")) == Term(Number(complex(0, 8)))
    assert processor.eval(AST("(6+5i) - (4+3i)")) == Term(Number(complex(2, 2)))
    assert processor.eval(AST("(3+7i) - (3+7i)")) == Term(Number())
    assert processor.eval(AST("(12+3i) - (12-1i)")) == Term(Number(complex(0, 4)))


def test_multiply_complex(processor, AST):
    assert processor.eval(AST("i*i")) == Term(Number(-1))
    assert processor.eval(AST("(2+3i)(1+4i)")) == Term(Number(complex(-10, 11)))
    assert processor.eval(AST("3(4-5i)")) == Term(Number(complex(12, -15)))
    assert processor.eval(AST("(-2+3i)(-1-4i)")) == Term(Number(complex(14, 5)))


def test_divide_complex(processor, AST):
    assert processor.eval(AST("(4+6i)/2")) == Term(Number(complex(2, 3)))
    assert processor.eval(AST("(8-4i)/-2")) == Term(Number(complex(-4, 2)))
    assert processor.eval(AST("(4+2i)/(1-i)")) == Term(Number(complex(1, 3)))
    assert processor.eval(AST("(6+3i)/(-2+i)")) == Term(Number(complex(-9, -12), 5))
    assert processor.eval(AST("(-2+i)/(2+3i)")) == Term(Number(complex(-1, 8), 13))
    assert processor.eval(AST("(3+4i)/(1-2i)")) == Term(Number(complex(-1, 2)))
    assert processor.eval(AST("0/(1+i)")) == Term(Number())


def test_numeric_exponentiation(processor, AST):
    # Exponentiation
    assert processor.eval(AST("5 ^ 2")) == Term(Number(25))
    assert processor.eval(AST("-3 ^ 2")) == Term(Number(-9))
    assert processor.eval(AST("(-3) ^ 2")) == Term(Number(9))
    assert processor.eval(AST("2 ^- 1")) == Term(Number("0.5"))

    # Perfect Radicals
    assert processor.eval(AST("2 √ 25")) == Term(Number(5))
    assert processor.eval(AST("2 √ 25")) == Term(Number(5))
    assert processor.eval(AST("2 √ -1")) == Term(Number(complex(imag=1)))
    assert processor.eval(AST("2 √ -81")) == Term(Number(complex(imag=9)))
    assert processor.eval(AST("3 √ 27")) == Term(Number(3))
    assert processor.eval(AST("3 √ -27")) == Term(Number(-3))

    # Imperfect radicals
    assert processor.eval(AST("2 √ 50")) == Term(Number(5), Number(2), Number(1, 2))
    assert processor.eval(AST("2 √ 192")) == Term(Number(8), Number(3), Number(1, 2))
    assert processor.eval(AST("3 √ 81")) == Term(Number(3), Number(3), Number(1, 3))
    assert processor.eval(AST("2 √ 27")) == Term(Number(3), Number(3), exp=Number(1, 2))
    assert processor.eval(AST("6 √ 27")) == Term(value=Number(3), exp=Number(1, 2))
    assert processor.eval(AST("4 √ -16")) == Term(Number(complex(imag=2)))
    assert processor.eval(AST("2 √ -128")) == Term(
        Number(complex(imag=8)), Number(2), Number(1, 2)
    )


def test_cancels_radical(processor, AST):
    # Simplify canceling radicals with like exponents
    assert processor.eval(AST("(2 √ -50)^2")) == Term(Number(-50))
    assert processor.eval(AST("(3 √ -81)^3")) == Term(Number(-81))
    assert processor.eval(AST("(2√5) * (2√5)")) == Term(Number(5))
    assert processor.eval(AST("(2√-5) * (2√5)")) == Term(Number(complex(imag=5)))
    assert processor.eval(AST("(2√32) * (2√2)")) == Term(Number(8))
    assert processor.eval(AST("(3√9) * (3√3)")) == Term(Number(3))

    # Simplify canceling radicals with like bases
    assert processor.eval(AST("27^(1/2) * 27^(-1/6)")) == Term(Number(3))
    assert processor.eval(AST("8^(1/2) * 8^(1/3)")) == Term(
        Number(4), Number(2), Number(1, 2)
    )
    assert processor.eval(AST("2(2√2) * 3√8")) == Term(
        Number(4), Number(2), Number(1, 2)
    )
    assert processor.eval(AST("4(2√2) * 2√8")) == Term(Number(16))


def test_multiply_radicals(processor, AST):
    assert processor.eval(AST("(2√27)(2√2)(1/(6√27))")) == Term(
        Number(3), Number(2), Number(1, 2)
    )
    assert processor.eval(AST("(2√8)(2√2)(1/(4√16))")) == Term(Number(2))
    assert processor.eval(AST("(2√50)(2√2)(1/(5√100))")) == Term(
        value=Number(1000), exp=Number(1, 5)
    )
    assert processor.eval(AST("(2√18)(2√2)(1/(3√9))")) == Term(
        Number(2), Number(3), Number(1, 3)
    )
    # NOTE: Writing it as 2(2√6)3(2√2)(1/(3√12)) will fail. Needs fix
    # The product class simplification should be aware of radical numbers
    assert processor.eval(AST("2(2√6) * 3(2√2) * (1/(3√12))")) == Term(
        Number(2),
        Product(
            [
                Term(value=Number(3), exp=Number(1, 2)),
                Term(value=Number(18), exp=Number(1, 3)),
            ]
        ),
    )
