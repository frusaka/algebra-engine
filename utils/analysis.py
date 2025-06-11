from __future__ import annotations
import itertools
from operator import itemgetter
from typing import Sequence, TYPE_CHECKING
from functools import cache

if TYPE_CHECKING:
    from datatypes import *

from collections import defaultdict


def groupby(iterable: Sequence[Term], var: Variable) -> tuple[Number, Term]:
    from datatypes import Term, Polynomial

    groups = defaultdict(list)
    for item in iterable:
        exp = item.get_exp(var)
        groups[exp].append(item / Term(value=var, exp=exp))
    return (
        (k, v[0] if len(v) == 1 else Term(value=Polynomial(v)))
        for k, v in groups.items()
    )


def quadratic(comp: Comparison, var: Variable) -> tuple[Term] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return its roots
    """
    from datatypes import (
        Collection,
        Comparison,
        Term,
        Number,
        ETNode,
        ETOperatorNode,
        ETOperatorType,
        ETQuadraticNode,
        steps,
    )

    val = (comp.left - comp.right).value
    if len(val) == 1:
        return
    a, b, *c = sorted(groupby(val, var), reverse=True)
    if len(c) > 1 or c and c[0][0] != 0 or a[0] / 2 != b[0]:
        return
    u = a[0] / 2
    a, b = a[1], b[1]
    c = c[0][1] if c else Term(Number(0))
    # Make the rhs 0
    if comp.right.value:
        steps.register(ETNode(comp - comp.right))
    discr = (b ** Term(Number(2)) - Term(Number(4)) * a * c) ** Term(Number(1, 2))
    den = Term(Number(2)) * a
    steps.register(ETQuadraticNode(var, a, b, c))

    neg, pos = (-b + discr) / den, (-b - discr) / den
    if u != 1:
        steps.register(ETNode(Comparison(var, Collection({neg, pos}))))
        steps.register(ETOperatorNode(ETOperatorType.SQRT, u, 2))
        neg, pos = neg ** Term(u**-1), pos ** Term(u**-1)
        if not u.numerator % 2:
            return (neg, -neg), (pos, -pos)
    return neg, pos


def perfect_square(vals: Sequence[Term]):
    from datatypes import Term, Number

    if len(vals) != 3:
        return

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


def difficulty_weight(term: Term, var: Variable) -> float:
    from datatypes import Variable, Product, Number

    if term.value.__class__ is Number:
        return 0.05
    res = 1
    if term.coef != 1:
        res += 0.05
    if term.value.__class__ is Variable:
        if term.exp.denominator != 1:
            res += term.exp.denominator * 1.3
        else:
            res += float(term.exp) * 1.2
        if term.value != var:
            return res * 0.4
        return res
    res += sum(difficulty_weight(term, var) for term in term.value)
    if term.value.__class__ is Product:
        return res * 1.2
    if term.exp != 1:
        res *= 1.1 * float(term.exp)
        if res < 0:
            return -res * 1.2
    return res


def next_eqn(
    equations: Sequence[Comparison], variables: Sequence[Variable]
) -> tuple[Comparison, Variable]:
    best = None
    best_score = float("inf")

    for eqn in equations:
        for var in variables:
            if not var in eqn:
                continue
            score = difficulty_weight(eqn.left - eqn.right, var)
            if score < best_score:
                best = (eqn, var)
                best_score = score
    if best is None:
        raise ValueError("No Equation containing ", ", ".join(variables))
    return best


def standard_form(collection: Sequence[Term]) -> list[Collection]:
    return sorted(collection, key=lexicographic_weight, reverse=1)
