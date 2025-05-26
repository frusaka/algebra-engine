from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from functools import cache

from utils.constants import STEPS

if TYPE_CHECKING:
    from datatypes import *


def quadratic(comp: Comparison, var: Variable) -> tuple[Term] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return its roots
    """
    from datatypes import Term, Number

    a, b = None, None
    x = Term(value=var)
    for t in comp.left.value:  # Must be a Polynomial
        v = t / x
        # Checks to detect a Quadratice
        # One term that when divided by x cancels the x
        if var not in v:
            if b:
                return
            b = v
            bx = t
        # One term that when divided by x^2 cancels the x
        elif var not in (v := v / x):
            if a:
                return
            a = v
            ax_2 = t
        # Should otherwise not contain x if not divisible by x or x^2
        elif var in t:
            return
    # Not a quadratic
    # For values like x^2-9=0, they can be solved without the quadratic formula
    if not (a and b):
        return
    # Make the rhs 0
    if comp.right.value:
        comp -= comp.right
        STEPS.append(comp.totex())
    # The rest of the boys, can even be another Polynomial
    c = comp.left - (ax_2 + bx)
    STEPS.append("\\text" + f"quadratic({a=}, {b=}, {c=})".join("{}"))
    discr = (b ** Term(Number(2)) - Term(Number(4)) * a * c) ** Term(Number(1, 2))
    den = Term(Number(2)) * a
    return (-b + discr) / den, (-b - discr) / den


def perfect_square(vals: Sequence[Term]):
    from datatypes import Term, Number

    if len(vals) == 3:
        a, b, c = standard_form(vals)
        root = Term(Number(1, 2))
        a **= root
        for b, c in [(b, c), (c, b)]:
            c = (c**root).scale(-1 if b.to_const() < 0 else 1)
            if vals == ((a + c) ** root.inv).value:
                return a + c


@cache
def lexicographic_weight(term: Term, alphabetic=True) -> Number:
    from datatypes import Number, Variable, Collection, Product

    if not isinstance(term.exp, Number) or (
        isinstance(term.value, Number) and term.exp == 1
    ):
        return 0
    res = 0

    if isinstance(term.value, Collection) and term.exp == 1:
        if alphabetic and term.remainder.value:
            return res - 100
        # Calling sum() does not work
        seen = {}
        for t in term.value:
            if not isinstance(t.exp, Number):
                continue
            v = lexicographic_weight(t, 0)
            if alphabetic:
                ext = lexicographic_weight(t, 1) - v
                if isinstance(term.value, Product):
                    v *= 0.9
                    ext *= 0.6
                v += ext
            seen[t.value] = max(v, seen.get(t.value, res))
        for i in seen.values():
            res += i
        return res
    res = float(term.exp)
    if isinstance(term.value, Variable) and alphabetic:
        # Map range formula
        a, b = ord("A"), ord("z")
        c, d = 0, 0.1
        x = ord(term.value)
        res += c + ((x - a) * (d - c)) / (b - a)
    if isinstance(term.value, Number):
        return -res
    return res


def difficulty_weight(term: Term) -> int:
    from datatypes import Number, Collection, Product

    if not isinstance(term.exp, Number) or isinstance(term.exp.numerator, complex):
        return 10
    res = 0

    if isinstance(term.value, Collection) and term.exp == 1:
        seen = {}
        for t in term.value:
            if not isinstance(t.exp, Number):
                seen[t] = 10
                continue
            seen[t.value] = max(difficulty_weight(t), seen.get(t.value, res))
        res += sum(seen.values())
        if isinstance(term.value, Product):
            res *= 1.6
        return res
    return abs(term.exp.numerator * term.exp.denominator)


def standard_form(collection: Sequence[Term]) -> list[Collection]:
    return sorted(collection, key=lexicographic_weight, reverse=1)
