import pytest
import gc
from parsing import parser
from datatypes import *
from utils import steps
from utils import clear_all_caches


def clear():
    clear_all_caches()
    gc.collect()


def walk(step):
    yield step
    for child in step.children:
        yield from walk(child)


@pytest.fixture(autouse=True)
def set_up_and_teardown():
    steps._steps.clear()
    steps.set_verbosity(True)
    yield
    clear()
    steps.set_verbosity(False)


def test_verborsity_toggle():
    steps.set_verbosity(False)
    expr = parser.eval("3+2-5")
    assert not steps._steps
    steps.set_verbosity(True)
    expr = parser.eval("3+2-5")
    assert steps._steps


def test_autodelete():
    parser.eval("3+2-5")
    clear()
    assert not steps._steps

    expr1 = parser.eval("3+x/(x+2)+1")
    clear()
    assert steps._steps
    del expr1
    assert not steps._steps

    eqn1 = parser.eval("3x^2-5=11")
    assert steps.explain(eqn1, False) is not None
    clear()
    assert steps.explain(eqn1, False) is not None
    del eqn1
    assert not steps._steps

    expr = parser.eval("factor(expand((a^4-b^4)(3x-4b+1)))")
    assert steps._steps
    assert steps.explain(expr, False) is not None
    clear()
    assert steps._steps
    del expr
    assert not steps._steps

    # Multiple expressions stored
    expr1 = parser.eval("factor(x^2-5+1)-3x+5")
    expr2 = parser.eval("1+1+1+1-5")
    n = len(steps._steps)
    assert n
    clear()
    assert len(steps._steps) != n  # Cleared some things
    del expr1
    clear()
    assert steps._steps and len(steps._steps) < n
    del expr2
    clear()
    assert not steps._steps


@pytest.mark.parametrize(
    "expr",
    [
        "1+1+1+1-5",
        "factor(expand((a^4-b^4)(x^3-5-3)^2))",
        "-3x^2 + 12x - 9 = 0",
        # "x-sqrt(x)/2>=0",
        "[x^2 + y^2 = 25, x^2 - 9 = y^2 - 2]",
    ],
)
def test_keeps_substeps(expr):
    expr = parser.eval(expr)
    clear()
    assert steps._steps
    hist = steps.explain(expr, False)
    assert hist is not None
    assert hist.children
    for n in walk(hist):
        assert n.result is not None or n.type.name == "STATE"


def test_simplifying_steps():
    x = Var("x")
    expr = 3 * x - 5 + 2
    hist = steps.explain(expr, False)
    assert hist == steps.Step("ADD", (3 * x - 5, 2), expr)
