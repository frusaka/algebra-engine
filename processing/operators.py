from dataclasses import dataclass
from operator import *
from data_types import Comparison, CompRel
from typing import Any
from utils.constants import SYMBOLS


@dataclass
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Any
    value: Any

    def __repr__(self):
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass
class Binary:
    """Unary operator: arithmetic (+-*/) or exponetiation"""

    oper: Any
    left: Any
    right: Any

    def __repr__(self):
        return f"({self.left} {SYMBOLS.get(self.oper.type.name)} {self.right})"


def eq(a, b):
    return Comparison(a, b)


def gt(a, b):
    return Comparison(a, b, CompRel.GT)


def lt(a, b):
    return Comparison(a, b, CompRel.LT)


def le(a, b):
    return Comparison(a, b, CompRel.LE)


def ge(a, b):
    return Comparison(a, b, CompRel.GE)


def getitem(a, b):
    return b[a.value]


def root(a, b):
    return b**a.inv


def bool(a):
    return getattr(a, "__bool__", lambda: a.value != 0)()
