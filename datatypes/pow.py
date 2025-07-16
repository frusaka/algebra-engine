from dataclasses import dataclass
import itertools
from functools import lru_cache, reduce
from typing import TYPE_CHECKING

import utils

from . import nodes
from .base import Collection, Node


@dataclass(frozen=True, init=False, slots=True)
class Pow(Node):
    base: Node
    exp: Node

    @lru_cache
    def __new__(cls, base: Node, exp: Node) -> Node:
        if base == 1:
            return base
        if base.__class__ is Pow:
            # May nullify constraints: √(x-2)^2 = |x-2|, not x-2
            base, exp = base.base, exp * base.exp
        if exp == 0:
            return nodes.Const(1)
        if exp == 1:
            return base
        c = 1
        if exp.__class__ is nodes.Const:
            if base.__class__ is nodes.Mul:
                return nodes.Mul.from_terms(t**exp for t in base.args)
            if isinstance(base, nodes.Number):
                if base.__class__ is nodes.Float:
                    return base.pow(exp)
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
            return nodes.Mul(self, c)
        return self

    if TYPE_CHECKING:

        def __init__(self, base: Node, exp: Node) -> None:
            pass

    def __repr__(self) -> str:
        base = str(self.base)
        if (
            isinstance(self.base, Collection)
            or self.base.__class__ is nodes.Const
            and self.base.denominator > 1
        ):
            base = base.join("()")
        if self.exp.__class__ is nodes.Const:
            p = utils.superscript(self.exp.numerator) if self.exp.numerator != 1 else ""
            base += p
            if self.exp.denominator != 1:
                r = (
                    utils.superscript(self.exp.denominator)
                    if self.exp.denominator != 2
                    else ""
                )
                base = r + "√" + base
            return base

        exp = str(self.exp)
        if isinstance(self.exp, Collection):
            exp = exp.join("()")
        return f"{base}^{exp}"

    def as_ratio(self) -> tuple[Node]:
        if self.exp.canonical()[0].is_neg():
            return (nodes.Const(1), Pow(self.base, -self.exp))
        return (self, nodes.Const(1))

    def simplify(self) -> Node:
        return Pow(self.base.simplify(), self.exp.simplify())

    def expand(self):
        if self.exp.canonical()[0].is_neg():
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
                    itertools.starmap(
                        nodes.Mul,
                        itertools.product(nodes.Add.flatten(a), nodes.Add.flatten(b)),
                    )
                ),
                itertools.repeat(base, exp.numerator),
            )
            if exp.denominator == 1:
                return base
            exp = nodes.Const(1, exp.denominator)
        return Pow(base, exp)

    def subs(self, mapping):
        return Pow(self.base.subs(mapping), self.exp.subs(mapping))

    def approx(self) -> float | complex:
        v = self.base.approx()
        e = self.exp.approx()
        if (
            self.exp.__class__ is nodes.Const
            and self.exp.denominator % 2
            and self.exp.denominator > 1
            and not v.imag
            and v < 0
        ):
            return -abs(v) ** e
        return v**e

    def totex(self):
        from .mul import _tex

        if not isinstance(self.exp, nodes.Const) or self.exp.denominator == 1:
            base = _tex(self.base).join("{}")
            exp = self.exp.totex().join("{}")
            return f"{base}^{exp}"
        base = self.base.totex()
        if self.exp.numerator != 1:
            base = _tex(self.base) + "^" + str(self.exp.numerator).join("{}")
        base = base.join("{}")
        r = self.exp.denominator
        if r == 2:
            return f"\\sqrt{base}"
        return f"\\sqrt[{r}]{base}"


__all__ = ["Pow"]
