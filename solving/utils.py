from __future__ import annotations
from itertools import product
from typing import Sequence, TYPE_CHECKING
from functools import cache

from datatypes import nodes
from .solutions import SolutionSet

from utils.factoring import flatten_factors
from utils.polynomial import is_polynomial

if TYPE_CHECKING:
    from datatypes.base import Node
    from datatypes.nodes import *
    from solving.comparison import Comparison

from collections import defaultdict


def groupby(iterable: Sequence[Node], var: Var) -> tuple[Const, Node]:
    groups = defaultdict(list)
    for item in iterable:
        exp = dict(flatten_factors(item)).get(var, 0)
        groups[exp].append(item / var**exp)
    return ((k, nodes.Add.from_terms(v)) for k, v in groups.items())


def quadratic(comp: Comparison, var: Var) -> tuple[Node] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return its roots
    """
    from solving.eval_trace import (
        ETSteps,
        ETNode,
        ETOperatorNode,
        ETQuadraticNode,
        ETOperatorType,
    )
    from solving.comparison import Comparison

    val = comp.left - comp.right
    if val.__class__ is not nodes.Add or not is_polynomial(val):
        return
    res = sorted(groupby(val, var), reverse=True)
    if len(res) <= 1 or any(var in i[1] for i in res):
        return

    a, b, *c = res
    if len(c) > 1 or c and c[0][0] != 0 or a[0] / 2 != b[0] or a[0] == 0:
        return
    u = nodes.Const(a[0], 2)
    a, b = a[1], b[1]
    c = c[0][1] if c else 0
    # Make the rhs 0
    if comp.right:
        ETSteps.register(ETNode(comp - comp.right))
    discr = ((b**2) - 4 * a * c) ** nodes.Const(1, 2)
    den = 2 * a
    ETSteps.register(ETQuadraticNode(var, a, b, c))

    neg, pos = (-b + discr) / den, (-b - discr) / den
    if u != 1:
        ETSteps.register(ETNode(Comparison(var, SolutionSet({neg, pos}))))
        if u > 1:
            ETSteps.register(ETOperatorNode(ETOperatorType.SQRT, u, 2))
        else:
            ETSteps.register(ETOperatorNode(ETOperatorType.POW, u**-1, 2))

        neg, pos = neg ** u.pow(-1), pos ** u.pow(-1)
        if not u.numerator % 2:
            return {neg, -neg, pos, -pos}
    return {neg, pos}


def difficulty_weight(term: Node, var: Var) -> float:
    if term.__class__ is nodes.Const:
        return 0.05
    res = 1
    if term.__class__ is nodes.Var:
        if term != var:
            return 0.4
        return 1
    if term.__class__ is nodes.Pow:
        if term.exp.denominator != 1:
            res = term.exp.denominator * 1.3
        else:
            res = float(term.exp) * 1.2
        res *= difficulty_weight(term.base, var)
        if term.base.__class__ is nodes.Add:
            return res * 1.1
        return res
    res = sum(difficulty_weight(term, var) for term in term)
    if term.__class__ is nodes.Mul:
        return res * 1.2
    return res


def next_eqn(
    equations: Sequence[Comparison], variables: Sequence[Var]
) -> tuple[Comparison, Var]:
    best = None
    best_score = float("inf")

    for eqn, var in product(equations, variables):
        if not var in eqn:
            continue
        score = difficulty_weight(eqn.left - eqn.right, var)
        if score < best_score:
            best = (eqn, var)
            best_score = score
    if best is None:
        raise ValueError("No Equation containing ", ", ".join(variables))
    return best


__all__ = ["next_eqn", "difficulty_weight", "quadratic"]
