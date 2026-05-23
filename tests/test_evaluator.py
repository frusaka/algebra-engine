from contextlib import contextmanager

import pytest
from datatypes.const import Const
from datatypes.var import Var
from parsing.parser import parse, Function
from unittest.mock import patch, MagicMock
import importlib

from parsing.tokens import TokenType
from solving.comparison import Comparison


@pytest.fixture
def mock_call():
    with patch.object(
        Function, "__call__", autospec=True, wraps=Function.__call__
    ) as caller:
        yield caller


@contextmanager
def spy(path: str):
    module_name, _, attr = path.rpartition(".")
    module = importlib.import_module(module_name)
    original = getattr(module, attr)

    def tracker(*args, **kwargs):
        value = original(*args, **kwargs)
        mocked.return_value = value
        return value

    with patch(path, wraps=tracker) as mocked:
        yield mocked


def test_arithmetic(mock_call):
    with spy("parsing.operators.neg") as neg:
        parse("-5")
        mock_call.assert_called_with(Function("neg", 5))
        neg.assert_called_once_with(5)
        parse("--5")
        neg.assert_called_with(-5)

    with spy("parsing.operators.mul") as mul:
        parse("2*3")
        mock_call.assert_called_with(Function("mul", 2, 3))
        mul.assert_called_once_with(2, 3)

    with spy("parsing.operators.div") as div:
        parse("2/3")
        mock_call.assert_called_with(Function("div", 2, 3))
        div.assert_called_once_with(2, 3)
    with spy("parsing.operators.add") as add:
        parse("x+z")
        mock_call.assert_called_with(Function("add", "x", "z"))
        add.assert_called_once_with("x", "z")
    with spy("parsing.operators.sub") as sub:
        parse("x-5")
        mock_call.assert_called_with(Function("sub", "x", 5))
        sub.assert_called_once_with("x", 5)


def test_nested_expressions(mock_call):
    with spy("parsing.operators.add") as add, spy("parsing.operators.mul") as mul:
        parse("2*3+4")
        assert len(mock_call.call_args_list) == 2
        mul.assert_called_once_with(2, 3)
        add.assert_called_once_with(mul.return_value, 4)
        mock_call.reset_mock()

    with spy("parsing.operators.sub") as sub, spy("parsing.operators.div") as div:
        parse("x-10/2")
        assert len(mock_call.call_args_list) == 2
        div.assert_called_once_with(10, 2)
        sub.assert_called_once_with("x", div.return_value)
        mock_call.reset_mock()

    with spy("parsing.operators.sqrt") as sqrt, spy("parsing.operators.add") as add:
        parse("sqrt(3, 8)+5")
        assert len(mock_call.call_args_list) == 2
        sqrt.assert_called_once_with(3, 8)
        add.assert_called_once_with(sqrt.return_value, 5)
        mock_call.reset_mock()

    with spy("parsing.operators.neg") as neg, spy("parsing.operators.mul") as mul:
        parse("-5*2")
        assert len(mock_call.call_args_list) == 2
        neg.assert_called_once_with(5)
        mul.assert_called_once_with(neg.return_value, 2)
        mock_call.reset_mock()


def test_comparison():
    for c, n in zip(
        ["eq", "lt", "le", "gt", "ge"],
        [5, 6, 12, 1, 21],
    ):
        with spy(f"parsing.operators.{c}") as comp:
            Function(c, Var("x"), Const(n))()
            comp.assert_called_once_with("x", n)


def test_system():
    x = Var("x")
    y = Var("y")
    with spy("parsing.operators.system") as sys:
        parse("[x+y=5, x-y=11]", False)
        sys.assert_called_once_with(
            Comparison(x + y, 5),
            Comparison(x - y, 11),
        )


def test_functions():
    x = Var("x")
    with spy("parsing.operators.sqrt") as sqrt:
        parse("sqrt(8)")
        sqrt.assert_called_once_with(None, 8)
    with spy("parsing.operators.gcd") as gcd:
        parse("gcd(12,8)")
        gcd.assert_called_once_with(12, 8)
    with spy("parsing.operators.lcm") as lcm:
        parse("lcm(12,8)")
        lcm.assert_called_once_with(12, 8)
    with spy("parsing.operators.factor") as factor:
        parse("factor(x^2+2x+1)")
        factor.assert_called_once_with(x**2 + 2 * x + 1)
    with spy("parsing.operators.expand") as expand:
        parse("expand((x+1)^2)")
        expand.assert_called_once_with((x + 1) ** 2)
    # with spy("parsing.operators.subs") as subs:
    #     parse("subs(x+3=5, x=3)")
    #     subs.assert_called_once_with(Comparison(x + 3, 5), Comparison(x, 3))
