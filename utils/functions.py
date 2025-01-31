from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data_types import Term, Number, Collection, Comparison, Variable


def lexicographic_weight(term: Term, alphabetic=True) -> Number:
    from data_types import Number, Variable, Collection

    if isinstance(term.value, Number) or not isinstance(term.exp, Number):
        return Number(0)
    res = Number(0)

    if isinstance(term.value, Collection) and term.exp == 1:
        # Calling sum() does not work
        for t in term.value:
            res += lexicographic_weight(t, alphabetic)
        return res
    res = term.exp
    if isinstance(term.value, Variable) and alphabetic:
        # Map range formula
        a, b = ord("A"), ord("z")
        c, d = 0, 0.1
        x = ord(term.value)
        res += c + ((x - a) * (d - c)) / (b - a)
    return res


def standard_form(collection: Collection) -> list[Collection]:
    return sorted(collection, key=lexicographic_weight, reverse=1)


def quadratic(comp: Comparison, var: Variable) -> tuple[Term] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return a tuple (a, b, c)
    """
    from data_types import Term, Comparison

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
    if not a or not b:
        return
    # Make the rhs 0
    if comp.right.value:
        comp = comp.reverse_sub(comp.right)
        print(comp)
    # The rest of the boys, can even be another Polynomial
    c = comp.left - (ax_2 + bx)
    return a, b, c


def quadratic_formula(a: Term, b: Term, c: Term) -> Term:
    """Apply the quadratic formula: (-b ± (b^2 - 4ac))/2a"""
    from data_types import Term, Number, Solutions

    print(
        f"q(a={a}, b={b}, c={c})",
        "(-b ± 2√(b^2 - 4ac))/2a",
        sep=" = ",
    )
    rhs = (b ** Term(Number(2)) - Term(Number(4)) * a * c) ** Term(Number("1/2"))
    den = Term(Number(2)) * a
    res = {(-b + rhs) / den, (-b - rhs) / den}
    if len(res) == 1:
        return res.pop()
    return Solutions(res)
