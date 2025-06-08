from datatypes import Number, Product, Term


def test_simplify_constants(processor):
    assert processor.eval("10 + 5 - 3") == Term(Number(12))
    assert processor.eval("20 - 4 + 2") == Term(Number(18))
    assert processor.eval("2 * 3 + 4") == Term(Number(10))
    assert processor.eval("10 / 2 + 5") == Term(Number(10))
    assert processor.eval("2^3 + 1") == Term(Number(9))
    assert processor.eval("(2 + 3) * 4") == Term(Number(20))
    assert processor.eval("10 / (2 + 3)") == Term(Number(2))
    assert processor.eval("2 * (3 + 4)") == Term(Number(14))
    assert processor.eval("(2 + 3) * (4 + 1)") == Term(Number(25))


def test_merge_complex(processor):
    assert processor.eval("(3+4i) + (1+2i)") == Term(Number(complex(4, 6)))
    assert processor.eval("5 + 3i") == Term(Number(complex(5, 3)))
    assert processor.eval("(6+2i) + (-6+6i)") == Term(Number(complex(0, 8)))
    assert processor.eval("(6+5i) - (4+3i)") == Term(Number(complex(2, 2)))
    assert processor.eval("(3+7i) - (3+7i)") == Term(Number())
    assert processor.eval("(12+3i) - (12-1i)") == Term(Number(complex(0, 4)))


def test_multiply_complex(processor):
    assert processor.eval("i*i") == Term(Number(-1))
    assert processor.eval("(2+3i)(1+4i)") == Term(Number(complex(-10, 11)))
    assert processor.eval("3(4-5i)") == Term(Number(complex(12, -15)))
    assert processor.eval("(-2+3i)(-1-4i)") == Term(Number(complex(14, 5)))


def test_divide_complex(processor):
    assert processor.eval("(4+6i)/2") == Term(Number(complex(2, 3)))
    assert processor.eval("(8-4i)/-2") == Term(Number(complex(-4, 2)))
    assert processor.eval("(4+2i)/(1-i)") == Term(Number(complex(1, 3)))
    assert processor.eval("(6+3i)/(-2+i)") == Term(Number(complex(-9, -12), 5))
    assert processor.eval("(-2+i)/(2+3i)") == Term(Number(complex(-1, 8), 13))
    assert processor.eval("(3+4i)/(1-2i)") == Term(Number(complex(-1, 2)))
    assert processor.eval("0/(1+i)") == Term(Number())


def test_numeric_exponentiation(processor):
    # Exponentiation
    assert processor.eval("5 ^ 2") == Term(Number(25))
    assert processor.eval("-3 ^ 2") == Term(Number(-9))
    assert processor.eval("(-3) ^ 2") == Term(Number(9))
    assert processor.eval("2 ^- 1") == Term(Number(1, 2))

    # Perfect Radicals
    assert processor.eval("25^0.5") == Term(Number(5))
    assert processor.eval("(-1)^0.5") == Term(Number(complex(imag=1)))
    assert processor.eval("(-81)^0.5") == Term(Number(complex(imag=9)))
    assert processor.eval("27^(1/3)") == Term(Number(3))
    assert processor.eval("(-27)^(1/3)") == Term(Number(-3))

    # Imperfect radicals
    assert processor.eval("50^0.5") == Term(Number(5), Number(2), Number(1, 2))
    assert processor.eval("192^0.5") == Term(Number(8), Number(3), Number(1, 2))
    assert processor.eval("81^(1/3)") == Term(Number(3), Number(3), Number(1, 3))
    assert processor.eval("27^0.5") == Term(Number(3), Number(3), exp=Number(1, 2))
    assert processor.eval("27^(1/6)") == Term(value=Number(3), exp=Number(1, 2))
    assert processor.eval("(-128)^0.5") == Term(
        Number(complex(imag=8)), Number(2), Number(1, 2)
    )
    # Edge cases: even radicals greater than 2
    assert processor.eval("(-1)^0.25") == Term(value=Number(-1), exp=Number(1, 4))
    assert processor.eval("(-16)^0.25") == Term(Number(2), Number(-1), Number(1, 4))
    assert processor.eval("(-27)^(1/6)") == Term(value=Number(-27), exp=Number(1, 6))


def test_multiply_radicals(processor):
    assert processor.eval("((-50)^0.5)^2") == Term(Number(-50))

    assert processor.eval("8^(1/2) * 8^(1/3)") == Term(
        Number(4), Number(2), Number(1, 2)
    )
    assert processor.eval("4(2^0.5) * 8^0.5") == Term(Number(16))
    assert processor.eval("(-5)^0.5 * (5)^0.5") == Term(Number(complex(imag=5)))

    assert processor.eval("27^0.5(1/27^(1/6))2^0.5") == Term(
        Number(3), Number(2), Number(1, 2)
    )
    assert processor.eval("(1/(16^0.25))8^0.5*2^0.5") == Term(Number(2))
    assert processor.eval("50^0.5(1/100^.2)2^0.5") == Term(
        value=Number(1000), exp=Number(1, 5)
    )
    assert processor.eval("18^0.5*2^0.5(1/9^(1/3))") == Term(
        Number(2), Number(3), Number(1, 3)
    )
    assert processor.eval("2(6^0.5) * 3(2^0.5) * (1/(12^(1/3)))") == Term(
        Number(6), Number(12), Number(1, 6)
    )
