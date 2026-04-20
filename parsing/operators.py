from datatypes.base import Node
from solving.comparison import CompRel, Comparison

from solving.solutions import *
from solving.system import System
from datatypes.nodes import *
from solving.core import solve

from utils import lcm, gcd


def add(a: Node, b: Node) -> Node:
    return a + b


def sub(a: Node, b: Node) -> Node:
    return a - b


def mul(a: Node, b: Node) -> Node:
    return a * b


def frac(a: Node, b: Node) -> Node:
    return a / b


def div(a: Node, b: Node) -> Node:
    return a / b


def pow(a: Node, b: Node) -> Node:
    return a**b


def pos(a: Node) -> Node:
    return a


def neg(a: Node) -> Node:
    return -a


def eq(a: Node, b: Node) -> Comparison:
    return Comparison(a, b)


def gt(a: Node, b: Node) -> Comparison:
    return Comparison(a, b, CompRel.GT)


def lt(a: Node, b: Node) -> Comparison:
    return Comparison(a, b, CompRel.LT)


def le(a: Node, b: Node) -> Comparison:
    return Comparison(a, b, CompRel.LE)


def ge(a: Node, b: Node) -> Comparison:
    return Comparison(a, b, CompRel.GE)


def subs(a: Node | Comparison | System, *eqns: Comparison):
    """Substitute all occurances of `var` with the provided value"""
    return a.subs(dict((eqn.left, eqn.right) for eqn in eqns))  # .expand()


def approx(a: Node) -> float | complex:
    return a.approx()


def sqrt(n: Node | None, a: Node) -> Node:
    if n is None:
        return a ** Const(1, 2)
    return a ** (Const(1) / n)


def expand(a: Node) -> Node:
    return a.expand()


def factor(a: Node) -> Node:
    return a.factor()
