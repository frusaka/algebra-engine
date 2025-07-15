from __future__ import annotations
import math
from typing import Sequence, TYPE_CHECKING
from functools import cache, lru_cache

import numpy as np

from datatypes import nodes
from solving.eval_trace import ETSteps
import utils
from .solutions import SolutionSet


if TYPE_CHECKING:
    from datatypes.base import Node
    from datatypes.nodes import *
    from solving.comparison import Comparison

from collections import defaultdict


def groupby(iterable: Sequence[Node], var: Var) -> tuple[Const, Node]:
    groups = defaultdict(list)
    for item in iterable:
        exp = dict(utils.mult_key(t, 1) for t in nodes.Mul.flatten(item, 0)).get(var, 0)
        groups[exp].append(item / var**exp)
    return ((k, nodes.Add.from_terms(v)) for k, v in groups.items())


def quadratic(f: tuple[Node]) -> tuple[Node] | None:
    """
    Find the roots of `val` given that it is a quadratic Polynomial,
    return its roots
    """

    a, b, c = f

    discr = ((b**2) - 4 * a * c) ** nodes.Const(1, 2)
    den = 2 * a
    return {(-b + discr) / den, (-b - discr) / den}


def roots_cubic(f):
    # Inspired by sympy/polys/polyroots.py
    # a*x**3 + b*x**2 + c*x + d -> x**3 + a*x**2 + b*x + c
    _, a, b, c = [i / f[0] for i in f]

    # x**3 + a*x**2 + b*x + c -> u**3 + p*u + q
    p = b - a**2 / 3
    q = 2 * a**3 / 27 - a * b / 3 + c
    Δ = (q / 2) ** 2 + (p / 3) ** 3
    w = (-1 + nodes.Const(3) ** 0.5 * 1j) / 2
    w2 = (-1 - nodes.Const(3) ** 0.5 * 1j) / 2
    s = [(-q / 2 + Δ**0.5) ** nodes.Const(1, 3)]
    s.extend(s[0] * i for i in (w, w2))
    return {(s - p / (3 * s) - a / 3).simplify() for s in s}


def nth_roots(vals, n):
    vals = {v ** nodes.Const(1, n) for v in vals}
    if not n % 2:
        vals.update(-v for v in tuple(vals))
    elif n == 3:
        w = (-1 + nodes.Const(3) ** 0.5 * 1j) / 2
        w2 = (-1 - nodes.Const(3) ** 0.5 * 1j) / 2
        vals.update(i for v in tuple(vals) for i in (v * w, v * w2))
    return vals


def roots(f: list[Node]):
    d = len(f) - 1
    u = math.gcd(*(d - i for i, c in enumerate(f) if c))

    if u > 1:
        f = tuple(f[idx] for idx in range(0, d + 1, u))
        d //= u
    else:
        u = 1
    if d == 2:
        return nth_roots(quadratic(f), u)
    if d == 3:
        return nth_roots(roots_cubic(f), u)
    try:
        return nth_roots(map(simplify_complex, np.roots([i.approx() for i in f])), u)
    except:
        raise ValueError("Multivariate high degree polynomial")


def simplify_complex(n: complex) -> Float:
    if abs(n.imag) <= 1e-12:
        return nodes.Float(float(n.real))
    return nodes.Float(complex(n))


def _sum(vals):
    return map(sum(zip(*vals)))


@lru_cache
def difficulty_weight(term: Node, var: Var) -> float:
    if isinstance(term, nodes.Number):
        return (0, 0, 0.01 + term.is_neg() * 0.01)

    if term.__class__ is nodes.Var:
        if term != var:
            return (0.1, 1, 0.2)
        return (1, 0, 0.05)
    if term.__class__ is nodes.Pow:
        if term.exp.denominator != 1:
            res = term.exp.denominator * term.exp.numerator * 1.3
        else:
            res = term.exp.numerator
        if res < 0:
            res *= -1.2
        return tuple(res * i for i in difficulty_weight(term.base, var))
    res = list(zip(*(difficulty_weight(term, var) for term in term)))
    if term.__class__ is nodes.Mul:
        return tuple(map(sum, res))
    return max(res[0]), sum(res[1]), sum(res[2]) / len(res)


def _sum(vals):
    return tuple(map(sum, zip(*vals)))


def arrange_eqns(eqns, vars):
    vars.sort(
        key=lambda v: _sum(difficulty_weight(eqn.left - eqn.right, v) for eqn in eqns),
    )
    res = {}
    for eqn in eqns:
        t = tuple(difficulty_weight(eqn.left - eqn.right, v) for v in vars)
        k = min(
            (t[idx] for idx in range(len(t)) if vars[idx] in eqn.expand()),
            default=(1e5, 1e5, 1e5),
            key=lambda k: (bool(k[1]), *k),
        )
        v = vars[t.index(k)] if k[0] != 1e5 else None
        #          (univariate, degree, nterms, extra-weight), key, variable
        res[eqn] = (bool(k[1]), k[0], k[1], int(k[-1]) * 10 / 10), t, v
    return res


def next_eqn(
    equations: Sequence[Comparison], variables: Sequence[Var]
) -> tuple[Comparison, Var]:
    vars = list(variables)
    eqns = list(equations)
    err_msg = "No independent Equation containing " + ", ".join(vars)
    if not eqns:
        raise ValueError(err_msg)

    weights = arrange_eqns(eqns, vars)
    best = min(weights, key=weights.get)
    _, _, v = weights[best]

    if v is None:
        raise ValueError(err_msg)
    return best, v


def domain_restriction(node, var: Var) -> tuple[Comparison]:
    from .comparison import Comparison, CompRel
    from .system import System

    system = []
    seen = {}
    tmp = {}

    def vars():
        alphabet = [chr(i) for i in range(ord("a"), ord("z") + 1)]
        start_index = alphabet.index(var.lower())
        i = 0
        while True:
            yield nodes.Var(alphabet[(start_index + i + 1) % 26])
            i += 1

    def visit(node, register):
        if node in seen:
            return seen[node]
        if node.__class__ is nodes.Pow and var in node:
            sub = visit(node.base, 0)

            r = not node.exp.denominator % 2
            f = node.exp.numerator < 0

            if f or r:
                if register:
                    rel = ("GE", "GT")[f] if r else "NE"
                    system.append(
                        Comparison(sub, nodes.Const(0), getattr(CompRel, rel))
                    )
                v = next(letters)
                tmp[v] = sub**node.exp
                seen[node] = v
            else:
                seen[node] = sub**node.exp
            return seen[node]
        elif isinstance(node, (nodes.Add, nodes.Mul)):
            return node.from_terms(visit(t, register) for t in node.args)
        seen[node] = node
        return node

    letters = vars()
    visit(node, 1)
    print(tmp, system)
    return tuple(system)


__all__ = [
    "next_eqn",
    "arrange_eqn",
    "domain_restriction",
    "difficulty_weight",
    "quadratic",
    "roots",
]
