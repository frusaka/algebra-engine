from dataclasses import dataclass
import itertools
from functools import lru_cache, reduce
from typing import TYPE_CHECKING

import utils

from . import nodes
from .base import Node


@dataclass(frozen=True, init=False, slots=True)
class Pow(Node):
    base: Node
    exp: Node

    @lru_cache
    def __new__(cls, base: Node, exp: Node) -> Node:
        if base == 1:
            return base
        if base.__class__ is Pow:
            base, exp = base.base, exp * base.exp
        if exp == 0:
            return nodes.Const(1)
        if exp == 1:
            return base
        c = 1
        if exp.__class__ is nodes.Const:
            if base.__class__ is nodes.Mul:
                return nodes.Mul.from_terms(t**exp for t in base.args)
            if base.__class__ is nodes.Const:
                if exp.denominator == 1:
                    return base.pow(exp.numerator)
                c, base, exp = utils.simplify_radical(
                    base.pow(exp.numerator), exp.denominator
                )
                if base == 1 or exp == 1:
                    return c
            elif base.__class__ is nodes.Add:
                c, base = base.cancel_gcd(normalize=exp < 0)
                c **= exp
        self = super(Pow, cls).__new__(cls)
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "exp", exp)
        if c != 1:
            return nodes.Mul.from_terms([self, c], 0)
        return self

    if TYPE_CHECKING:

        def __init__(self, base: Node, exp: Node) -> None:
            pass

    def __repr__(self) -> str:
        if self.exp.__class__ is nodes.Const:
            p = utils.superscript(self.exp.numerator) if self.exp.numerator != 1 else ""
            v = str(self.base)
            v += p
            if self.exp.denominator != 1:
                r = (
                    utils.superscript(self.exp.denominator)
                    if self.exp.denominator != 2
                    else ""
                )
                v = r + "√" + v
                if r:
                    v = v.join("()")
            return v
        exp = str(self.exp)
        if exp.__class__ is nodes.Mul:
            exp = exp.join("()")
        return f"{self.base}^{exp}"

    def as_numer_denom(self) -> tuple[Node]:
        if self.exp.canonical()[0] < 0:
            return (nodes.Const(1), Pow(self.base, -self.exp))
        return (self, nodes.Const(1))

    def canonical(self):
        return nodes.Const(1), self

    def simplify(self) -> Node:
        return Pow(self.base.simplify(), self.exp.simplify())

    def expand(self):
        if self.exp.canonical()[0] < 0:
            return Pow(Pow(self.base, -self.exp).expand(), nodes.Const(-1))
        base = self.base.expand()
        exp = self.exp.expand()
        if (
            base.__class__ is nodes.Add
            and exp.__class__ is nodes.Const
            and not exp.numerator.imag
            and exp.numerator > 1
        ):
            base = reduce(
                lambda a, b: nodes.Add.from_terms(
                    itertools.starmap(nodes.Mul, itertools.product(a, b))
                ),
                itertools.repeat(base, exp.numerator),
            )
            if exp.denominator == 1:
                return base
            exp = nodes.Const(1, exp.denominator)
        return Pow(base, exp)

    def ast_subs(self, mapping):
        if self in mapping:
            return mapping[self]
        return Pow(self.base.ast_subs(mapping), self.exp.ast_subs(mapping))

    def domain_restriction(self, var):
        if not self.exp.denominator % 2 and var in str(self.base):
            return [(self.base, "GE")]
        if self.exp.numerator < 0 and var in self.base:
            return [(self.base, "NE")]
        return []

    def approx(self) -> float | complex:
        return self.base.approx() ** self.exp.approx()


__all__ = ["Pow"]
