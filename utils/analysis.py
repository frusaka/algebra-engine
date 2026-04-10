from __future__ import annotations

from typing import TYPE_CHECKING

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


def get_vars(node: Node) -> set[Var]:
    """
    Get the immedieate variables from an expression.
    Only goes up to depth 1:
        meaning if some variables are deeply nested, they are skipped
    """
    return set(
        mult_key(v)
        for i in nodes.Add.flatten(node)
        for v in nodes.Mul.flatten(i)
        if mult_key(v).__class__ is nodes.Var
    )
