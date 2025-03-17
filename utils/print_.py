from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datatypes import Comparison, Number


def print_frac(frac: Number) -> str:
    denominator = frac.denominator
    if denominator == 1:
        return str(frac.numerator)
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if denominator == 1 and "e" not in (v := str(frac.numerator / frac.denominator)):
        return v
    return "/".join((str(frac.numerator), str(frac.denominator)))


def print_coef(coef: Number) -> str:
    res = ""
    if coef != 1:
        res = str(coef)
        if not coef.numerator.real:
            res = res.join("()")
    if coef == -1:
        res = "-"
    return res


def ineq_to_range(ineq: Comparison) -> str:
    left, right = "(", ")"
    if ineq.rel.name.startswith("G"):
        if ineq.rel.name.endswith("E"):
            left = "["
        return left + str(ineq.right)
    if ineq.rel.name.endswith("E"):
        right = "]"
    return str(ineq.right) + right
