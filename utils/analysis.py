from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

import math
from itertools import zip_longest
from functools import lru_cache, reduce

from datatypes import nodes

if TYPE_CHECKING:
    from datatypes.nodes import *
    from datatypes.base import Node


def mult_key(v: Node, exp=False):
    match v.__class__.__name__:
        case "Const" | "Float":
            if exp:
                return None, v
            return v
        case "Pow":
            # Must revisit
            if exp:
                if isinstance(v.base, nodes.Number) and isinstance(v.exp, nodes.Number):
                    return nodes.Const, (v.base, v.exp)

                return v.base, v.exp
            return v.base
    if exp:
        return v, nodes.Const(1)
    return v


@lru_cache
def order_key(node: Node) -> tuple:
    match node.__class__.__name__:
        case "Const" | "Float":
            return (0, 0)
        case "Var":
            return (1, ord("z") * len(node) - sum(map(ord, node)))
        case "Pow":
            if node.exp.__class__ is not nodes.Const:
                return (0, 0, *order_key(node.base), *order_key(node.exp))
            if node.exp.denominator != 1:
                return (-1, float(node.exp), *order_key(node.base))
            return tuple(
                map(
                    lambda v: math.prod(v) * 1.0001,
                    zip_longest(
                        (node.exp.numerator,), order_key(node.base), fillvalue=1
                    ),
                )
            )
        case "Mul":
            return tuple(
                reduce(
                    lambda a, b: map(sum, zip_longest(a, b, fillvalue=0)),
                    map(order_key, node.args),
                ),
            )

        case "Add":
            res = list(max(map(order_key, node.args)))
            res[1] *= 0.5
            res[-1] += len(node.args)
            return tuple(res)
    raise TypeError("Unsupported type", node, type(node))


def ordered_terms(args: Iterable[Node], reverse=False) -> list[Node]:
    args = list(args)
    key = order_key
    if reverse:
        m = max(map(order_key, args))[0]
        key = lambda t: (m - order_key(t)[0], *order_key(t)[1:])
    args.sort(key=key, reverse=True)
    return args


@lru_cache
def get_vars(node: Node) -> frozenset[Var]:
    """
    Get the immedieate variables from an expression.
    Only goes up to depth 1:
        meaning if some variables are deeply nested, they are skipped
    """
    return frozenset(
        mult_key(v)
        for i in nodes.Add.flatten(node)
        for v in nodes.Mul.flatten(i)
        if mult_key(v).__class__ is nodes.Var
    )
