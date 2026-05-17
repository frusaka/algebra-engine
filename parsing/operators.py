from datatypes.base import Expr
from solving.comparison import CompRel, Comparison

from solving.solutions import *
from solving.system import System
from datatypes.expr import *
from solving.core import solve

from utils import lcm, gcd, factor


def add(a: Expr, b: Expr) -> Expr:
    return a + b


def sub(a: Expr, b: Expr) -> Expr:
    return a - b


def mul(a: Expr, b: Expr) -> Expr:
    return a * b


def frac(a: Expr, b: Expr) -> Expr:
    return a / b


def div(a: Expr, b: Expr) -> Expr:
    return a / b


def pow(a: Expr, b: Expr) -> Expr:
    return a**b


def pos(a: Expr) -> Expr:
    return a


def neg(a: Expr) -> Expr:
    return -a


def eq(a: Expr, b: Expr) -> Comparison:
    return Comparison(a, b)


def gt(a: Expr, b: Expr) -> Comparison:
    return Comparison(a, b, CompRel.GT)


def lt(a: Expr, b: Expr) -> Comparison:
    return Comparison(a, b, CompRel.LT)


def le(a: Expr, b: Expr) -> Comparison:
    return Comparison(a, b, CompRel.LE)


def ge(a: Expr, b: Expr) -> Comparison:
    return Comparison(a, b, CompRel.GE)


def subs(a: Expr | Comparison | System, *eqns: Comparison):
    """Substitute all occurances of `var` with the provided value"""
    return a.subs(dict((eqn.left, eqn.right) for eqn in eqns))  # .expand()


def approx(a: Expr) -> float | complex:
    return a.approx()


def sqrt(n: Expr | None, a: Expr) -> Expr:
    if n is None:
        return a ** Const(1, 2)
    return a ** (Const(1) / n)


def expand(a: Expr) -> Expr:
    return a.expand()
