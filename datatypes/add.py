from __future__ import annotations
from typing import Iterable, TYPE_CHECKING

import math
import itertools
from collections import defaultdict
from functools import lru_cache

from .base import Node, Collection
from . import nodes
import utils


@lru_cache
def order_key(node: Node) -> tuple:
    # Format: (Exponent, Type, *Value)
    if isinstance(node, nodes.Number):
        if node.__class__ is nodes.Float:
            return (0, 0, 0, str(node._val))
        if node.numerator.imag:
            return (0, 0, 0, str(node))
        return (0, 0, node)
    if node.__class__ is nodes.Var:
        return (1, 4, ord("z") * len(node) - sum(map(ord, node)))
    if node.__class__ is nodes.Pow:
        deg = order_key(node.exp)
        deg = deg[2] if deg[1] == 0 and deg[2] else 1
        return (
            deg * order_key(node.base)[0],
            3,
            order_key(node.exp),
            order_key(node.base),
        )
    order = tuple(map(order_key, node.args))
    if node.__class__ is nodes.Mul:
        if len(order) == 2 and order[0][1] == 0:
            return (*order[1], order[0][1:])
        return (sum(i[0] for i in order), 2, order[::-1])
    return (max(i[0] for i in order), 1, order)


def ordered_terms(args: Iterable[Node]) -> list[Node]:
    return sorted(args, key=order_key, reverse=True)


class Add(Collection):
    if TYPE_CHECKING:

        def __init__(self, *args: Node, rationalize=True): ...

    @lru_cache
    def __repr__(self) -> str:
        res = ""
        for i in self.args:
            v = repr(i)
            if not res:
                res = v
                continue
            op = " + "
            if v.startswith("-"):
                op = " - "
                v = str(-i)
                # v = v[1:]
            res += op + v
        return res

    @staticmethod
    def sort_terms(args) -> list[Node]:
        return ordered_terms(args)

    @classmethod
    def merge(cls, args, rationalize=True) -> list[Node]:
        def form(k, v):
            if k is None:
                return v
            return nodes.Mul(k, v)

        def calculate(k, v):
            if k is None:
                return den * v
            if den.__class__ is nodes.Add and utils.is_polynomial(den):
                n, d = k.as_ratio()
                if utils.is_polynomial(n) and utils.is_polynomial(d):
                    return utils.cancel_factors(den.multiply(v * n), d)
            return nodes.Mul(den, v, k)

        groups = defaultdict(nodes.Const)
        frac = False
        for term in args:
            coef, val = term.canonical()
            groups[val] = groups[val].add(coef)
            if not frac and val and utils.hasremainder(val):
                frac = True
            if groups[val] == 0:
                groups.pop(val)

        if not rationalize or not frac or len(groups) == 1:
            return ordered_terms(itertools.starmap(form, groups.items())) or [
                nodes.Const(0)
            ]
        # Get the LCM
        den = nodes.Const(1)
        for k in groups:
            if k is None:
                den *= groups[k].denominator
                continue
            den = utils.lcm(den, k.as_ratio()[1])
        # Combine
        num = Add.from_terms(calculate(k, v) for k, v in groups.items())  # .expand()
        # return list(Add.flatten(num.simplify() / den.simplify()))
        return list(Add.flatten(num / den))

    def as_ratio(self):
        c, a = self.cancel_gcd()
        n, d = c.as_ratio()
        return (a.multiply(n), nodes.Const(d))

    def simplify(self) -> Node:
        return utils.factor(self)

    def expand(self) -> Node:
        return Add.from_terms(node.expand() for node in self)

    def cancel_gcd(self, normalize=True) -> tuple[Node, Add]:
        den = math.lcm(*(i.canonical()[0].denominator for i in self))
        if (
            # normalize and
            utils.is_polynomial(self)
            and self.args[0].canonical()[0].is_neg()
        ):
            den *= -1
        if den != 1:
            self = self.multiply(den)
        gcd = utils.gcd(*self, light=True)

        if gcd == den == 1:
            return gcd, self
        # if isinstance(gcd, nodes.Add):
        #     g = dict(itertools.chain(*map(utils.flatten_factors, gcd.cancel_gcd())))
        # else:
        #     g = dict(utils.flatten_factors(gcd))

        # return gcd / den, Add.from_terms(
        #     nodes.Mul.from_terms(
        #         k ** (v - g.get(k, 0)) for k, v in utils.flatten_factors(n)
        #     )
        #     for n in self
        # )
        return gcd / den, self.multiply(gcd**-1)

    def divide(self, b: Add) -> Node:
        if self == b:
            return nodes.Const(1)
        if not (
            utils.is_polynomial(self) and utils.is_polynomial(b) and b.__class__ is Add
        ):
            # return self.multiply(b**-1)
            return nodes.Mul(self, b**-1)
        return utils.cancel_factors(self, b)

    def multiply(self, b: Node) -> Add:
        if b.__class__ is nodes.Add:
            return Add.from_terms(i * j for i in self for j in b)
        return Add.from_terms(i * b for i in self)

    def totex(self):
        res = ""
        for term in self:
            rep = term.totex()
            if res:
                if str(term.canonical()[0]).startswith("-"):
                    res += "-"
                    rep = (-term).totex()
                else:
                    res += "+"
            res += rep
        return res


__all__ = ["Add"]
