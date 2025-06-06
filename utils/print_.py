from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datatypes import Comparison, Number
    from processing import ETNode


def print_frac(frac: Number) -> str:
    """Convert a fraction to a string representation, omitting the denominator if it is 1."""
    from processing import Interpreter

    denominator = frac.denominator
    if denominator == 1:
        return str(frac.numerator)

    res = "/".join((str(frac.numerator), str(frac.denominator)))
    if not Interpreter.instance().print_frac_auto:
        return res
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if denominator == 1 and "e" not in (v := str(frac.numerator / frac.denominator)):
        return v
    return res


def print_coef(coef: Number, tex=False) -> str:
    """Convert a coefficient to a string representation, choosing to omit 1 or -1."""
    res = ""
    if coef != 1:
        res = str(coef)
        if not tex and not coef.numerator.real:
            res = res.join("()")
    if coef == -1:
        res = "-"
    return res


def ineq_to_range(ineq: Comparison) -> str:
    """Convert an inequality to a range representation."""
    left, right = "(", ")"
    if ineq.rel.name.startswith("G"):
        if ineq.rel.name.endswith("E"):
            left = "["
        return left + str(ineq.right)
    if ineq.rel.name.endswith("E"):
        right = "]"
    return str(ineq.right) + right


def ineq_to_range_tex(ineq: Comparison) -> str:
    """Convert an inequality to a LaTeX range representation."""
    left, right = "\\left(", "\\right)"
    if ineq.rel.name.startswith("G"):
        if ineq.rel.name.endswith("E"):
            left = "\\left\\lbrack "
        return left + ineq.right.totex()
    if ineq.rel.name.endswith("E"):
        right = "\\right\\rbrack "
    return ineq.right.totex() + right
