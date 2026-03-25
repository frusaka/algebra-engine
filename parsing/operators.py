from typing import Any
from operator import *
from datatypes.base import Node
from solving.comparison import CompRel, Comparison

from solving.solutions import *
from solving.system import System
from datatypes.nodes import *
from solving.core import solve
from utils import lcm, gcd, factor


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


def subs(a: Node | Comparison, *eqns: Comparison) -> Node | Comparison:
    """Substitute all occurances of `var` with the provided value"""
    return a.subs(dict((eqn.left, eqn.right) for eqn in eqns))  # .expand()


def approx(a: Any) -> Comparison | float | complex | Any:
    if isinstance(a, tuple):
        return tuple(map(approx, a))
    return a.approx()


def sqrt(a: Node, b=2) -> Node:
    return a ** (Const(1) / b)


def expand(a):
    return a.expand()
