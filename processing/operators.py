from typing import Any, Sequence
from operator import *
from datatypes.base import Node
from solving.comparison import CompRel, Comparison

from solving.solutions import *
from solving.system import System
from datatypes.nodes import *
from solving.core import solve


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


def subs(a: Node | Comparison, mapping: dict[Var, Node]) -> Node | Comparison:
    """Substitute all occurances of `var` with the provided value"""
    return a.ast_subs(mapping).expand()


def approx(a: Any) -> Comparison | float | complex | Any:
    if a.__class__ is Comparison:
        return Comparison(a.left, approx(a.right), a.rel)
    if isinstance(a, tuple):
        return tuple(map(approx, a))
    return a.approx()


def sqrt(a: Node) -> Node:
    return a ** Const(1, 2)
