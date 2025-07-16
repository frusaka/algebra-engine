from __future__ import annotations
import itertools
import math
from typing import Iterable

from . import nodes
from .base import Node, Collection
from functools import lru_cache, reduce
from collections import defaultdict

import utils


def form(k, v):
    if k is nodes.Const:
        k, v = v
    if not v:
        return
    if k is None:
        if v == 1:
            return
        return v
    return nodes.Pow(k, v)


def gr_mul(vals):
    pows = defaultdict(lambda: nodes.Const(1))
    for i in sorted(vals, key=lambda t: utils.mult_key(t).__class__ is nodes.Add):
        if i.__class__ is nodes.Pow:
            k, v = i.exp, i.base
        else:
            k, v = nodes.Const(1), i
        pows[k] = v.multiply(pows[k])
    return sorted(
        (nodes.Pow(v, k) for k, v in pows.items()),
        key=lambda t: t.__class__ is not nodes.Add,
    )


def combine_numeric_radicals(groups: dict, v: tuple[Node]):
    k = nodes.Const
    if k not in groups:
        groups[k] = v
        return

    b, exp_b = groups[k]
    v, exp_v = v
    exp = math.lcm(exp_b.denominator, exp_v.denominator)
    c, v, exp = utils.simplify_radical(
        v ** (exp // exp_v.denominator) * b ** (exp // exp_b.denominator), exp
    )
    groups[None] = c.mul(groups.get(None, 1))
    groups.pop(k)
    if exp != v != 1:
        groups[k] = v, exp


def _str(n: Node):
    res = str(n)
    if isinstance(n, nodes.Add) or (isinstance(n, nodes.Pow) and res[0].isdigit()):
        res = res.join("()")
    return res


def _tex(n: Node):
    res = n.totex()
    if isinstance(n, Collection):
        return res.join("()")
    return res


class Mul(Collection):
    @lru_cache
    def __repr__(self) -> str:
        # return "*".join(map(str, utils.ordered_terms(self, True)))
        num, den = self.as_ratio()
        if num.__class__ is Mul:
            c, num = num.canonical()
            num = utils.print_coef(c) + "".join(
                map(_str, (utils.ordered_terms(Mul.flatten(num, 0), True)))
            )

        else:
            num = _str(num)
        if den.__class__ is Mul:
            c, den = den.canonical()
            den = utils.print_coef(c) + "".join(
                map(_str, (utils.ordered_terms(Mul.flatten(den, 0), True)))
            )
            den = den.join("()")
        else:
            den = _str(den)
            if den == "1":
                den = ""
        if not den:
            return num
        return "/".join((num, den))

    def as_ratio(self) -> tuple[Node]:
        return tuple(map(Mul.from_terms, zip(*(t.as_ratio() for t in self))))

    @classmethod
    def merge(cls, args: Iterable[Node]) -> list[Node]:
        res = defaultdict(nodes.Const)
        for k, v in (utils.mult_key(n, True) for n in args):
            if k is None:
                if v == 0:
                    return [v]
                res[k] = v.mul(res.get(k, 1))
                continue
            if k is nodes.Const:
                combine_numeric_radicals(res, v)
            else:
                res[k] += v
        res = list(filter(bool, itertools.starmap(form, res.items())))
        # Automatically distribute constant factor
        if len(res) == 2 and set(map(type, res)) == {nodes.Add, nodes.Const}:
            return [res.pop().multiply(res.pop())]
        return res or [nodes.Const(1)]

    def simplify(self) -> Node:
        return Mul.from_terms(i.simplify() for i in self.args)

    def expand(self) -> Node:
        num, den = self.as_ratio()
        mul = lambda a, b: a.multiply(b)
        num = reduce(mul, (num.expand() for num in Mul.flatten(num)))
        den = reduce(mul, (den.expand() for den in Mul.flatten(den)))
        if den.__class__ is nodes.Add:
            return num.divide(den)
        if den == 1:
            return num
        return num.multiply(den**-1)

    def canonical(self) -> tuple[Node, Node]:
        if c := next((i for i in self.args if i.__class__ is nodes.Const), 0):
            args = list(self.args)
            args.remove(c)
            if len(args) == 1:
                return c, args[0]
            return c, Mul.from_terms(args, 0)
        return nodes.Const(1), self

    def totex(self) -> str:
        num, den = self.as_ratio()
        if num.__class__ is Mul:
            c, num = num.canonical()
            num = utils.print_coef(c).replace("i", "\\mathrm{i}") + "".join(
                map(_tex, (utils.ordered_terms(Mul.flatten(num, 0), True)))
            )

        else:
            num = _tex(num)
        if den.__class__ is Mul:
            c, den = den.canonical()
            den = utils.print_coef(c).replace("i", "\\mathrm{i}") + "".join(
                map(_tex, (utils.ordered_terms(Mul.flatten(den, 0), True)))
            )
        else:
            den = _tex(den)
            if den == "1":
                den = ""
        if not den:
            return num

        return f"\\frac{num.join("{}")}{den.join("{}")}"


__all__ = ["Mul"]
