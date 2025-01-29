from processing import AST
from data_types import Number, AlgebraObject


def test_simplify_constants(processor):
    assert processor.eval(AST("10 + 5 - 3")) == AlgebraObject(Number(12))
    assert processor.eval(AST("20 - 4 + 2")) == AlgebraObject(Number(18))
    assert processor.eval(AST("2 * 3 + 4")) == AlgebraObject(Number(10))
    assert processor.eval(AST("10 / 2 + 5")) == AlgebraObject(Number(10))
    assert processor.eval(AST("2^3 + 1")) == AlgebraObject(Number(9))
    assert processor.eval(AST("(2 + 3) * 4")) == AlgebraObject(Number(20))
    assert processor.eval(AST("10 / (2 + 3)")) == AlgebraObject(Number(2))
    assert processor.eval(AST("2 * (3 + 4)")) == AlgebraObject(Number(14))
    assert processor.eval(AST("(2 + 3) * (4 + 1)")) == AlgebraObject(Number(25))


def test_merge_complex(processor):
    assert processor.eval(AST("(3+4i) + (1+2i)")) == AlgebraObject(
        Number(complex(4, 6))
    )
    assert processor.eval(AST("5 + 3i")) == AlgebraObject(Number(complex(5, 3)))
    assert processor.eval(AST("(6+2i) + (-6+6i)")) == AlgebraObject(
        Number(complex(0, 8))
    )
    assert processor.eval(AST("(6+5i) - (4+3i)")) == AlgebraObject(
        Number(complex(2, 2))
    )
    assert processor.eval(AST("(3+7i) - (3+7i)")) == AlgebraObject(Number())
    assert processor.eval(AST("(12+3i) - (12-1i)")) == AlgebraObject(
        Number(complex(0, 4))
    )


def test_multiply_complex(processor):
    assert processor.eval(AST("i*i")) == AlgebraObject(Number(-1))
    assert processor.eval(AST("(2+3i)(1+4i)")) == AlgebraObject(
        Number(complex(-10, 11))
    )
    assert processor.eval(AST("3(4-5i)")) == AlgebraObject(Number(complex(12, -15)))
    assert processor.eval(AST("(-2+3i)(-1-4i)")) == AlgebraObject(
        Number(complex(14, 5))
    )


def test_divide_complex(processor):
    assert processor.eval(AST("(4+6i)/2")) == AlgebraObject(Number(complex(2, 3)))
    assert processor.eval(AST("(8-4i)/-2")) == AlgebraObject(Number(complex(-4, 2)))
    assert processor.eval(AST("(4+2i)/(1-i)")) == AlgebraObject(Number(complex(1, 3)))
    assert processor.eval(AST("(6+3i)/(-2+i)")) == AlgebraObject(
        Number(complex(-9, -12), 5)
    )
    assert processor.eval(AST("(-2+i)/(2+3i)")) == AlgebraObject(
        Number(complex(-1, 8), 13)
    )
    assert processor.eval(AST("(3+4i)/(1-2i)")) == AlgebraObject(Number(complex(-1, 2)))
    assert processor.eval(AST("0/(1+i)")) == AlgebraObject(Number())
