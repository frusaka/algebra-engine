import pytest
from datatypes.const import Const
from datatypes.var import Var
from parsing.parser import eval, validate
from parsing import operators
from unittest.mock import patch

from parsing.tokens import TokenType
from solving.comparison import Comparison
from solving.system import System


@pytest.fixture
def mock_validate():
    with patch(
        "parsing.parser.validate",
        side_effect=lambda func, *args, **kwargs: func(*args, **kwargs),
    ) as validate:
        yield validate


def test_validate_inputs():
    # Representation of all data types
    n = Const(1)
    x = Var("x")
    m = x * 2
    a = x + 2
    p = x**2
    c = Comparison(x, p)
    s = System([c, Comparison(n, a)])
    t = m, a
    # fmt: off
    bin_funcs = ["add", "sub", "mul", "div", "pow", "sqrt", "eq", "lt", "le", "gt", "ge"]
    un_funcs = ["factor", "expand", "neg", "pos", "approx"]
    inv_bin_pairs = [(n, c), (s, c), (c, s), (a, s), (s, a), (c, t), (t, c), (p, s), (s, p)]
    val_bin_pairs = [(n, n), (n, m), (m, n), (m, m), (a, n), (n, a), (a, a), (a, m), (m, a), (p, n), (n, p), (p, a), (a, p), (p, m), (m, p), (p, p)]
    # fmt: on
    # Validates binary operators
    for f in bin_funcs:
        func = getattr(operators, f)
        # No argument Or passing None
        with pytest.raises(SyntaxError):
            validate(func, call=False)
        with pytest.raises(SyntaxError):
            validate(func, None, call=False)
        for i in inv_bin_pairs:
            # One argument
            with pytest.raises(SyntaxError):
                validate(func, i[0], call=False)
            with pytest.raises(TypeError):
                validate(func, *i, call=False)
        for i in val_bin_pairs:
            validate(func, *i, call=False)

    # Validates Unary operators
    for f in un_funcs:
        func = getattr(operators, f)
        with pytest.raises(SyntaxError):
            validate(func, call=False)
        for i in [c, s, t]:
            with pytest.raises(TypeError):
                validate(func, i, call=False)
        for i in [n, x, m, a, p]:
            validate(func, i, call=False)

    # LCM and GCD
    for func in [operators.lcm, operators.gcd]:
        with pytest.raises(ValueError):
            validate(func)
        for i, j in zip(inv_bin_pairs, val_bin_pairs):
            with pytest.raises(TypeError):
                validate(func, *i, call=False)
            with pytest.raises(TypeError):
                validate(func, *i, *j, call=False)
            validate(func, *j, call=False)
            validate(func, *j, *j, call=False)

    # Validates solve
    for i in (n, m, a, p, s, t, c):
        with pytest.raises(TypeError):
            validate(operators.solve, s, i, call=False)
        with pytest.raises(TypeError):
            validate(operators.solve, c, i, call=False)
    validate(operators.solve, s, x, call=False)
    validate(operators.solve, c, x, call=False)

    # Validates subsitution
    for i in (x, n, m, a, p, s, c):
        validate(operators.subs, i, c, call=False)
        validate(operators.subs, i, c, *s, call=False)
    with pytest.raises(SyntaxError):
        validate(operators.subs, call=False)
    with pytest.raises(TypeError):
        validate(operators.subs, t, call=False)

    for i in val_bin_pairs:
        with pytest.raises(TypeError):
            validate(operators.solve, *i, call=False)
        with pytest.raises(TypeError):
            validate(operators.subs, *i, call=False)


def test_arithmetic(mock_validate):
    with patch("parsing.operators.neg") as neg:
        neg.return_value = Const(-5)
        eval("-5")
        mock_validate.assert_called_with(neg, 5)
        neg.assert_called_once_with(5)
        eval("--5")
        neg.assert_called_with(-5)

    with patch("parsing.operators.mul") as mul:
        eval("2*3")
        mock_validate.assert_called_with(mul, 2, 3)
        mul.assert_called_once_with(2, 3)

    with patch("parsing.operators.div") as div:
        eval("2/3")
        mock_validate.assert_called_with(div, 2, 3)
        div.assert_called_once_with(2, 3)
    with patch("parsing.operators.add") as add:
        eval("x+z")
        mock_validate.assert_called_with(add, "x", "z")
        add.assert_called_once_with("x", "z")
    with patch("parsing.operators.sub") as sub:
        eval("x-5")
        mock_validate.assert_called_with(sub, "x", 5)
        sub.assert_called_once_with("x", 5)


def test_nested_expressions(mock_validate):
    with patch("parsing.operators.add") as add, patch("parsing.operators.mul") as mul:
        mul.return_value = Const(6)
        eval("2*3+4")
        assert len(mock_validate.call_args_list) == 2
        assert mock_validate.call_args_list[0].args == (mul, 2, 3)
        assert mock_validate.call_args_list[1].args == (add, mul.return_value, 4)
        mock_validate.reset_mock()
        mul.assert_called_once_with(2, 3)
        add.assert_called_once_with(mul.return_value, 4)

    with patch("parsing.operators.sub") as sub, patch("parsing.operators.div") as div:
        div.return_value = Const(-5)
        eval("x-10/2")
        assert len(mock_validate.call_args_list) == 2
        assert mock_validate.call_args_list[0].args == (div, 10, 2)
        assert mock_validate.call_args_list[1].args == (sub, "x", div.return_value)
        mock_validate.reset_mock()
        div.assert_called_once_with(10, 2)
        sub.assert_called_once_with("x", div.return_value)

    with patch("parsing.operators.sqrt") as sqrt, patch("parsing.operators.add") as add:
        sqrt.return_value = Const(2)
        eval("sqrt(3, 8)+5")
        assert len(mock_validate.call_args_list) == 2
        assert mock_validate.call_args_list[0].args == (sqrt, 3, 8)
        assert mock_validate.call_args_list[1].args == (add, sqrt.return_value, 5)
        mock_validate.reset_mock()
        sqrt.assert_called_once_with(3, 8)
        add.assert_called_once_with(sqrt.return_value, 5)

    with patch("parsing.operators.neg") as neg, patch("parsing.operators.mul") as mul:
        neg.return_value = Const(-5)
        eval("-5*2")
        assert len(mock_validate.call_args_list) == 2
        assert mock_validate.call_args_list[0].args == (neg, 5)
        assert mock_validate.call_args_list[1].args == (mul, neg.return_value, 2)
        mock_validate.reset_mock()
        neg.assert_called_once_with(5)
        mul.assert_called_once_with(neg.return_value, 2)


def test_comparison(mock_validate):
    with patch("parsing.operators.eq") as eq:
        eval("x=5", False)
        mock_validate.assert_called_with(eq, "x", 5)
        eq.assert_called_once_with("x", 5)
    with patch("parsing.operators.lt") as lt:
        eval("x<6", False)
        mock_validate.assert_called_with(lt, "x", 6)
        lt.assert_called_once_with("x", 6)
    with patch("parsing.operators.le") as le:
        eval("x<=12", False)
        mock_validate.assert_called_with(le, "x", 12)
        le.assert_called_once_with("x", 12)
    with patch("parsing.operators.gt") as gt:
        eval("x>1", False)
        mock_validate.assert_called_with(gt, "x", 1)
        gt.assert_called_once_with("x", 1)
    with patch("parsing.operators.ge") as ge:
        eval("x>=21", False)
        mock_validate.assert_called_with(ge, "x", 21)
        ge.assert_called_once_with("x", 21)


def test_system():
    x = Var("x")
    y = Var("y")
    with patch("parsing.operators.System") as sys:
        eval("[x+y=5, x-y=11]", False)
        assert len(sys.call_args.args) == 1 and tuple(sys.call_args.args[0]) == (
            Comparison(x + y, 5),
            Comparison(x - y, 11),
        )


def test_functions(mock_validate):
    x = Var("x")
    with patch("parsing.operators.sqrt") as sqrt:
        eval("sqrt(8)")
        mock_validate.assert_called_with(sqrt, TokenType.NaN, 8)
        sqrt.assert_called_once_with(TokenType.NaN, 8)
    with patch("parsing.operators.gcd") as gcd:
        eval("gcd(12,8)")
        mock_validate.assert_called_with(gcd, 12, 8)
        gcd.assert_called_once_with(12, 8)
    with patch("parsing.operators.lcm") as lcm:
        eval("lcm(12,8)")
        mock_validate.assert_called_with(lcm, 12, 8)
        lcm.assert_called_once_with(12, 8)
    with patch("parsing.operators.factor") as factor:
        eval("factor(x^2+2x+1)")
        mock_validate.assert_called_with(factor, x**2 + 2 * x + 1)
        factor.assert_called_once_with(x**2 + 2 * x + 1)
    with patch("parsing.operators.expand") as expand:
        eval("expand((x+1)^2)")
        mock_validate.assert_called_with(expand, (x + 1) ** 2)
        expand.assert_called_once_with((x + 1) ** 2)
    with patch("parsing.operators.subs") as subs:
        eval("subs(x+3=5, x=3)")
        mock_validate.assert_called_with(subs, Comparison(x + 3, 5), Comparison(x, 3))
        subs.assert_called_once_with(Comparison(x + 3, 5), Comparison(x, 3))
