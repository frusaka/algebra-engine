from __future__ import annotations
import itertools
import math
from typing import TYPE_CHECKING, Iterable

from . import expr
from .base import Expr, Collection
from .add import order_key as standard_key
from functools import reduce
from collections import defaultdict

import utils


def form(k, v):
    if k is expr.Const:
        k, v = v
    if not v:
        return
    if k is None:
        if v == 1:
            return
        return v
    return expr.Pow(k, v)


def gr_mul(vals):
    pows = defaultdict(lambda: expr.Const(1))
    for i in sorted(vals, key=lambda t: utils.mult_key(t).__class__ is expr.Add):
        if i.__class__ is expr.Pow:
            k, v = i.exp, i.base
        else:
            k, v = expr.Const(1), i
        pows[k] = v.multiply(pows[k])
    return sorted(
        (expr.Pow(v, k) for k, v in pows.items()),
        key=lambda t: t.__class__ is not expr.Add,
    )


def combine_numeric_radicals(groups: dict, v: tuple[Expr]):
    k = expr.Const
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


def _str(n: Expr):
    res = str(n)
    if isinstance(n, expr.Add) or (isinstance(n, expr.Pow) and res[0].isdigit()):
        res = res.join("()")
    return res


def _tex(n: Expr):
    res = n.totex()
    if isinstance(n, Collection):
        return res.join("()")
    return res


@utils.lru_cache
def order_key(node: Expr) -> tuple:
    # Format: (a, b, *c)
    # a = Type priority: Numbers, then Variables, then Power and so on
    # b = Exponent  weight (not degree)
    #     This is so that Pow first inherits the priorty of the base
    #     e.g x(y + 5)(x + 2)^2 is prefered over x(x + 2)^2(y + 5)
    # *c = Extra type-specific weight
    if isinstance(node, expr.Number):
        if node.__class__ is expr.Float:
            return (0, 0, 0, str(node._val))
        if node.numerator.imag:
            return (0, 0, 0, str(node))
        return (0, 0, node)
    if node.__class__ is expr.Var:
        return (1, 1, str(node))
    if node.__class__ is expr.Pow:
        return (order_key(node.base)[0], 2, order_key(node.exp), order_key(node.base))
    if node.__class__ is expr.Mul:
        return (3, 1, tuple(map(order_key, node.args))[::-1])
    return (4, 1, standard_key(node))


def ordered_terms(args: Iterable[Expr]) -> list[Expr]:
    return sorted(args, key=order_key)


class Mul(Collection):
    if TYPE_CHECKING:

        def __init__(self, *args: Expr, distr_const=True): ...

    @utils.lru_cache
    def __repr__(self) -> str:
        # return "*".join(map(str, utils.ordered_terms(self, True)))
        num, den = self.as_ratio()
        if num.__class__ is Mul:
            c, num = num.canonical()
            num = utils.print_coef(c) + "".join(map(_str, Mul.flatten(num, 0)))

        else:
            num = _str(num)
        if den.__class__ is Mul:
            c, den = den.canonical()
            den = utils.print_coef(c) + "".join(map(_str, Mul.flatten(den, 0)))
            den = den.join("()")
        else:
            den = _str(den)
            if den == "1":
                den = ""
        if not den:
            return num
        return "/".join((num, den))

    def as_ratio(self) -> tuple[Expr]:
        return tuple(
            map(
                lambda vals: Mul.from_terms(vals, distr_const=False),
                zip(*(t.as_ratio() for t in self)),
            )
        )

    @staticmethod
    def sort_terms(args) -> list[Expr]:
        return ordered_terms(args)

    @classmethod
    def merge(cls, args: Iterable[Expr], distr_const=True) -> list[Expr]:
        res = defaultdict(expr.Const)
        for k, v in (utils.mult_key(n, True) for n in args):
            if k is None:
                if v == 0:
                    return [v]
                res[k] = v.mul(res.get(k, 1))
                continue
            if k is expr.Const:
                combine_numeric_radicals(res, v)
            else:
                res[k] += v

        res = ordered_terms(filter(bool, itertools.starmap(form, res.items())))
        # Automatically distribute constant factor
        if (
            distr_const
            and len(res) == 2
            and set(map(type, res)) == {expr.Add, expr.Const}
        ):
            return [res.pop().multiply(res.pop())]
        return res or [expr.Const(1)]

    def _expand(self) -> Expr:
        num, den = self.as_ratio()
        num = reduce(Expr.multiply, (num._expand() for num in Mul.flatten(num)))
        den = reduce(Expr.multiply, (den._expand() for den in Mul.flatten(den)))
        if den == 1:
            return num
        if den.__class__ is expr.Add:
            return num.divide(den)
        return num.multiply(den**-1)

    def canonical(self) -> tuple[Expr, Expr]:
        if not isinstance(self.args[0], expr.Number):
            return (expr.Const(1), self)
        if len(self.args) == 2:
            return self.args
        return self.args[0], Mul.from_terms(self.args[1:], 0)

    def totex(self) -> str:
        num, den = self.as_ratio()
        if num.__class__ is Mul:
            c, num = num.canonical()
            num = utils.print_coef(c).replace("i", "\\mathrm{i}") + "".join(
                map(_tex, Mul.flatten(num, 0))
            )

        else:
            num = num.totex()
        if den.__class__ is Mul:
            c, den = den.canonical()
            den = utils.print_coef(c).join(("\\mathrm{", "}")) + "".join(
                map(_tex, Mul.flatten(den, 0))
            )
        else:
            den = den.totex()
            if den == "1":
                den = ""
        if not den:
            return num

        return f'\\frac{num.join("{}")}{den.join("{}")}'


__all__ = ["Mul"]
