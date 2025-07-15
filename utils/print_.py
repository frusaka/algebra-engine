from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datatypes.nodes import Const
    from solving.comparison import Comparison


def print_frac(frac: Const) -> str:
    """Convert a fraction to a string representation, omitting the denominator if it is 1."""

    denominator = frac.denominator
    if denominator == 1:
        return str(frac.numerator)

    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    if not frac.numerator.imag:
        cond = len(str(frac.numerator % frac.denominator / frac.denominator)) <= 4
    else:
        cond = (
            len(str(frac.numerator.imag % frac.denominator / frac.denominator))
        ) <= 4

    if denominator == 1 and cond:
        return str(frac.numerator / frac.denominator)
    return "{0}/{1}".format(frac.numerator, frac.denominator)


def print_coef(coef: Const) -> str:
    """Convert a coefficient to a string representation"""
    if coef == 1:
        return ""
    if coef == -1:
        return "-"
    return str(coef)


def superscript(n: int):
    return str(n).translate(str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"))


def print_system(equations: list[str]):
    res = ["⎧ " + equations[0]]
    for eq in equations[1:-1]:
        res.append("⎪ " + eq)
    if len(equations) > 1:
        res.append("⎩ " + equations[-1])
    return " \n" + "\n".join(res)


def truncate(text, max_length=80):
    if len(text) <= max_length:
        return text
    return text[: max_length - 2] + "…"
