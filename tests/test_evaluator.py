import pytest
from datatypes.const import Const
from datatypes.var import Var
from parsing.parser import eval
from unittest.mock import patch

from solving.comparison import Comparison


def test_arithmetic():
    with patch("parsing.operators.neg") as neg:
        neg.return_value = Const(-5)
        eval("-5")
        neg.assert_called_once_with(5)
        eval("--5")
        neg.assert_called_with(-5)

    with patch("parsing.operators.mul") as mul:
        eval("2*3")
        mul.assert_called_once_with(2, 3)
    with patch("parsing.operators.truediv") as div:
        eval("2/3")
        div.assert_called_once_with(2, 3)
    with patch("parsing.operators.add") as add:
        eval("x+z")
        add.assert_called_once_with("x", "z")
    with patch("parsing.operators.sub") as sub:
        eval("x-5")
        sub.assert_called_once_with("x", 5)


def test_nested_expressions():
    with patch("parsing.operators.add") as add, patch("parsing.operators.mul") as mul:
        mul.return_value = Const(6)
        eval("2*3+4")
        mul.assert_called_once_with(2, 3)
        add.assert_called_once_with(mul.return_value, 4)

    with patch("parsing.operators.sub") as sub, patch(
        "parsing.operators.truediv"
    ) as div:
        div.return_value = Const(-5)
        eval("x-10/2")
        div.assert_called_once_with(10, 2)
        sub.assert_called_once_with("x", div.return_value)

    with patch("parsing.operators.sqrt") as sqrt, patch("parsing.operators.add") as add:
        sqrt.return_value = Const(2)
        eval("sqrt(4)+5")
        sqrt.assert_called_once_with(4)
        add.assert_called_once_with(sqrt.return_value, 5)

    with patch("parsing.operators.neg") as neg, patch("parsing.operators.mul") as mul:
        neg.return_value = Const(-5)
        eval("-5*2")
        neg.assert_called_once_with(5)
        mul.assert_called_once_with(neg.return_value, 2)


def test_comparison():
    with patch("parsing.operators.eq") as eq:
        eval("x=5", False)
        eq.assert_called_once_with("x", 5)
    with patch("parsing.operators.lt") as lt:
        eval("x<5", False)
        lt.assert_called_once_with("x", 5)
    with patch("parsing.operators.le") as le:
        eval("x<=5", False)
        le.assert_called_once_with("x", 5)
    with patch("parsing.operators.gt") as gt:
        eval("x>5", False)
        gt.assert_called_once_with("x", 5)
    with patch("parsing.operators.ge") as ge:
        eval("x>=5", False)
        ge.assert_called_once_with("x", 5)


def test_system():
    x = Var("x")
    y = Var("y")
    with patch("parsing.operators.System") as sys:
        eval("[x+y=5, x-y=11]", False)
        assert len(sys.call_args.args) == 1 and tuple(sys.call_args.args[0]) == (
            Comparison(x + y, 5),
            Comparison(x - y, 11),
        )


def test_functions():
    x = Var("x")
    with patch("parsing.operators.sqrt") as sqrt:
        eval("sqrt(8)")
        sqrt.assert_called_once_with(8)
    with patch("parsing.operators.gcd") as gcd:
        eval("gcd(12,8)")
        gcd.assert_called_once_with(12, 8)
    with patch("parsing.operators.lcm") as lcm:
        eval("lcm(12,8)")
        lcm.assert_called_once_with(12, 8)
    with patch("parsing.operators.factor") as factor:
        eval("factor(x^2+2x+1)")
        factor.assert_called_once_with(x**2 + 2 * x + 1)
    with patch("parsing.operators.expand") as expand:
        eval("expand((x+1)^2)")
        expand.assert_called_once_with((x + 1) ** 2)
    with patch("parsing.operators.subs") as subs:
        eval("subs(x+3=5, x=3)")
        subs.assert_called_once_with(Comparison(x + 3, 5), Comparison(x, 3))
