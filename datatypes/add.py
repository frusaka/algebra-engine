from __future__ import annotations

import math
import itertools
from collections import defaultdict
from functools import lru_cache

from .base import Node, Collection
from . import nodes
import utils


class Add(Collection):
    @lru_cache
    def __repr__(self) -> str:
        res = ""
        for i in utils.ordered_terms(self.args):
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
            return list(itertools.starmap(form, groups.items())) or [nodes.Const(0)]

        # Get the LCM
        den = nodes.Const(1)
        for k in groups:
            if k is None:
                den *= groups[k].denominator
                continue
            den = utils.lcm(den, k.as_ratio()[1])
        # Combine
        num = Add.from_terms(calculate(k, v) for k, v in groups.items())  # .expand()
        den = den  # .expand()

        # if num.__class__ is nodes.Add:
        #     return list(Add.flatten(num.expand().divide(den)))
        return list(Add.flatten(num / den))

    def simplify(self) -> Node:
        return utils.factor(self.expand())

    def expand(self) -> Node:
        return Add.from_terms(node.expand() for node in self)

    def cancel_gcd(self, normalize=True) -> tuple[Node, Add]:
        den = math.lcm(*(i.canonical()[0].denominator for i in self))
        if (
            # normalize and
            utils.is_polynomial(self)
            and utils.leading(self).canonical()[0].is_neg()
        ):
            den *= -1
        if den != 1:
            self = self.multiply(den)
        gcd = utils.gcd(*self)

        if gcd == den == 1:
            return gcd, self
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

    def canonical(self) -> tuple[Node, Add]:
        return nodes.Const(1), self

    def totex(self):
        res = ""
        for term in utils.ordered_terms(self):
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
