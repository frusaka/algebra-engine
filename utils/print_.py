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
    if not frac.numerator.imag:
        cond = len(str(frac.numerator % frac.denominator / frac.denominator)) <= 5
    else:
        cond = (
            max(
                len(str(frac.numerator.real % frac.denominator / frac.denominator)),
                len(str(frac.numerator.imag % frac.denominator / frac.denominator)),
            )
            <= 5
        )
    if denominator == 1 and cond:
        return str(frac.numerator / frac.denominator)
    return res


def print_coef(coef: Number) -> str:
    """Convert a coefficient to a string representation"""
    if coef == 1:
        return ""
    if coef == -1:
        return "-"
    return str(coef)


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


def superscript(n: int):
    return str(n).translate(str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"))


def print_system(equations: list[str]):
    res = ["⎧ " + equations[0]]
    for eq in equations[1:-1]:
        res.append("⎪ " + eq)
    if len(equations) > 1:
        res.append("⎩ " + equations[-1])
    return " \n" + "\n".join(res)
