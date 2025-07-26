import webview
import operator
from enum import Enum
from fractions import Fraction

from datatypes.base import Node
from datatypes.nodes import *
from solving.core import solve
from solving.comparison import *
from solving.system import System
from solving.eval_trace import ETSteps
import utils


class macro:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self.func(*args)


class Macros(Enum):
    ImaginaryUnit = Const(1j)
    Nothing = None
    Complex = macro(lambda r, i: Add(r, i * 1j))
    num = macro(lambda x: Const(*Fraction(x).as_integer_ratio()))

    Add = Add
    Multiply = Mul
    Power = Pow
    Rational = Divide = macro(operator.truediv)

    Negate = macro(operator.neg)
    Sqrt = macro(lambda x: Pow(x, Const(1, 2)))
    Root = macro(lambda x, n: Pow(x, n**-1))

    Equal = Comparison
    Less = macro(lambda a, b: Comparison(a, b, CompRel.LT))
    LessEqual = macro(lambda a, b: Comparison(a, b, CompRel.LE))
    List = macro(lambda *vals: System(vals))
    solve = macro(solve)

    approx = macro(lambda x: x.approx())
    factor = macro(lambda x: x.simplify())
    expand = macro(lambda x: x.expand())
    GCD = macro(utils.gcd)
    LCM = macro(utils.lcm)

    def inspect(self, args):
        if self is Macros.List:
            return all(isinstance(i, Comparison) and i.rel is CompRel.EQ for i in args)
        if self is Macros.solve:
            return isinstance(args[0], (Comparison, System)) and (
                len(args) == 1
                or all(isinstance(i, str) and len(i) == 1 for i in args[1:])
            )
        if self is Macros.num:
            return len(args) == 1 and isinstance(args[0], str)
        return all(isinstance(i, Node) for i in args)

    def __call__(self, *args):
        assert self.inspect(
            args
        ), f"operator '{self.name}' had unexpected argument types"
        return self.value(*args)


def parse_mathJSON(expr):
    if isinstance(expr, str):
        if expr in Macros.__members__:
            return Macros[expr].value
        if expr == "NaN":
            raise ZeroDivisionError()
        if len(expr) > 1:
            raise ValueError(f"Unexpected symbol '{expr}'")
        return Var(expr)
    if isinstance(expr, float):
        return Const(*Fraction(str(expr)).as_integer_ratio())
    if isinstance(expr, int):
        return Const(expr)
    if isinstance(expr, dict):
        k, v = expr.popitem()
        if k == "num":
            return Macros.num(v)

    oper = expr[0]
    if len(expr) < 2:
        raise TypeError(f"{oper} operator has insufficient operands")
    if oper == "Error":
        raise SyntaxError("Error parsing latex")
    if not oper in Macros.__members__:
        raise SyntaxError(f"Unexpected operator '{oper}'")
    if oper == "solve":
        # No parsing variables just to be mean
        return Macros.solve(parse_mathJSON(expr[1]), *expr[2:])
    return Macros[oper](*map(parse_mathJSON, expr[1:]))


class API:
    def evaluate(self, expr):
        Comparison.solve_for.cache_clear()
        ETSteps.clear()
        res, err = "", ""
        # print(expr)
        try:
            res = parse_mathJSON(expr)
            res = res.totex().join(("$$", "$$")) if hasattr(res, "totex") else str(res)
        except Exception as e:
            # raise
            res = ""
            err = repr(e)
        steps = ETSteps.toHTML()
        return dict(steps=steps, error=err, final=res)


if __name__ == "__main__":
    webview.create_window(
        "Algebra Engine",
        "web/index.html",
        text_select=True,
        width=650,
        height=600,
        min_size=(400, 400),
        js_api=API(),
    )
    webview.start()
