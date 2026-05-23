from __future__ import annotations

from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from functools import lru_cache as cache
from . import expr

if TYPE_CHECKING:
    from datatypes.base import Expr
    from datatypes.var import Var


def mult_key(v: Expr, exp=False):
    match v.__class__.__name__:
        case "Const" | "Float":
            if exp:
                return None, v
            return v
        case "Pow":
            # Must revisit
            if exp:
                if isinstance(v.base, expr.Number) and isinstance(v.exp, expr.Number):
                    return expr.Const, (v.base, v.exp)

                return v.base, v.exp
            return v.base
    if exp:
        return v, expr.Const(1)
    return v


def get_vars(node: Expr) -> set[Var]:
    """
    Get the immedieate variables from an expression.
    Only goes up to depth 1:
        meaning if some variables are deeply nested, they are skipped
    """

    return set(
        mult_key(v)
        for i in expr.Add.flatten(node)
        for v in expr.Mul.flatten(i)
        if mult_key(v).__class__ is expr.Var
    )


CACHED_FUNCS = []
P = ParamSpec("P")
R = TypeVar("R")


def lru_cache(func: Callable[P, R]) -> Callable[P, R]:
    # For testing purposes
    func = cache(func)
    CACHED_FUNCS.append(func)
    return func


def clear_all_caches():
    for f in CACHED_FUNCS:
        f.cache_clear()


__all__ = ["mult_key", "get_vars", "lru_cache", "clear_all_caches"]
