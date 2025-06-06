from __future__ import annotations
from typing import Sequence, TYPE_CHECKING
from functools import cache

if TYPE_CHECKING:
    from datatypes import *


def quadratic(comp: Comparison, var: Variable) -> tuple[Term] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return its roots
    """
    from datatypes import Term, Number, ETNode, ETTextNode, steps

    a, b = None, None
    u = 1
    x = Term(value=var)
    x_2 = x ** Term(Number(2))
    left = [i for i in comp.left.value if var in i]
    if len(left) != 2:
        return
    ax_2, bx = sorted(left, key=lambda x: x.get_exp(var), reverse=True)
    if (
        ax_2.get_exp(var) / 2 != bx.get_exp(var)
        or ax_2.get_exp(var).__class__ is not Number
    ):
        return
    if var not in (bx / x_2).denominator and var not in (ax_2 / x_2).denominator:
        u = ax_2.get_exp(var) / 2
        a = ax_2 / Term(value=var, exp=u * 2)
        b = bx / Term(value=var, exp=u)
        u = Term(u**-1)
    else:
        a, b = ax_2 / x_2, bx / x
    # Make the rhs 0
    if comp.right.value:
        comp -= comp.right
        steps.register(ETNode(comp))
    # The rest of the boys, can even be another Polynomial
    c = comp.left - (ax_2 + bx)
    steps.register(
        ETTextNode("With Quadratic formula", "#0d80f2")
    )  # ({a=}, {b=}, {c=})"))
    discr = (b ** Term(Number(2)) - Term(Number(4)) * a * c) ** Term(Number(1, 2))
    den = Term(Number(2)) * a
    neg, pos = (-b + discr) / den, (-b - discr) / den
    if u != 1:
        # Needs to be registered to the steps as well
        neg, pos = neg**u, pos**u
        if not u.value.denominator % 2:
            return (neg, -neg), (pos, -pos)
    return neg, pos


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


# Make this consider what variable being solved for
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
