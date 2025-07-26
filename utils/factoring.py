from __future__ import annotations

from collections import Counter, defaultdict
import math
from typing import TYPE_CHECKING, Generator

from itertools import chain, product
from functools import lru_cache, reduce
from operator import itemgetter

from datatypes import nodes

from .numeric import primes
from .analysis import mult_key, get_vars
from .polynomial import (
    hasremainder,
    is_polynomial,
    degree,
    long_division,
    square_free,
    synthetic_divide,
)

if TYPE_CHECKING:
    from datatypes.nodes import *
    from datatypes.base import Node


@lru_cache
def flatten_factors(expr: Node) -> tuple[tuple[Node]]:
    if expr.__class__ is nodes.Mul:
        return tuple(i for arg in expr for i in flatten_factors(arg))
    if expr.__class__ is nodes.Const:
        if not expr.numerator.imag:
            return tuple(primes(expr).items())
        if not expr.numerator.real:
            res = {nodes.Const(1j): 1}
            res.update(primes(nodes.Const(expr.numerator.imag, expr.denominator)))
            return tuple(res.items())
        if (g := math.gcd(int(expr.numerator.real), int(expr.numerator.imag))) > 1:
            res = {nodes.Const(res.numerator / g): 1}
            res.update(primes(nodes.Const(g, expr.denominator)))
            return tuple(res.items())
    if expr.__class__ is nodes.Pow:
        return ((expr.base, expr.exp),)
    return ((expr, nodes.Const(1)),)


def _divisors(node: Node) -> Generator[Node, None, None]:
    primes = list(flatten_factors(node))
    exponents = [range(e.numerator + 1) for _, e in primes]
    yield from (
        reduce(
            lambda acc, pair: acc * (pair[0] ** pair[1]),
            zip((base for base, _ in primes), powers),
            nodes.Const(1),
        )
        for powers in product(*exponents)
    )
    yield nodes.Const(1)


@lru_cache
def divisors(node: Node) -> tuple[Node]:
    primes = list(flatten_factors(node))
    exponents = [range(e.numerator + 1) for _, e in primes]
    return tuple(
        reduce(
            lambda acc, pair: acc * (pair[0] ** pair[1]),
            zip((base for base, _ in primes), powers),
            nodes.Const(1),
        )
        for powers in product(*exponents)
    )
    # yield nodes.Const(1)
    # return tuple(_divisors(node))


def gcd(*args: Node, light=False) -> Node:
    """Greatest Common Divisor of a and b"""
    # Find factor by traversing the node tree
    if light or not all(n.__class__ is nodes.Add and is_polynomial(n) for n in args):
        factors = [
            {k: v // 1 for k, v in flatten_factors(n)}
            for n in chain(*map(nodes.Add.flatten, args))
        ]
        common = reduce(lambda a, b: a & b, map(dict.keys, factors))
        return nodes.Mul.from_terms(
            t ** min(map(itemgetter(t), factors), key=abs) for t in common
        )

    # Guaranteed to be working on two or more polynomials
    a = args[0]
    for b in args[1:]:
        if degree(b) > degree(a):
            a, b = b, a
        # Find common factor (Euclidean GCD)
        while b:
            q, r = long_division(a, b)
            if not q or r and r.__class__ is not nodes.Add:
                return nodes.Const(1)
            a, b = b, r

    return a.cancel_gcd()[1]


def lcm(a: Node, b: Node) -> Node:
    """Lowest Common Multiple of a & b"""
    if a == b:
        return a
    if not (
        a.__class__ is b.__class__ is nodes.Add
        and is_polynomial(a)
        and is_polynomial(b)
    ):
        return (a * b) / gcd(a, b)
    return cancel_factors(a.multiply(b), gcd(a, b))


def cancel_factors(a: Add, b: Node) -> Node:
    """
    Perform Polynomial division on `a` with `b` by cancelling factors
    """
    fac = gcd(a, b)
    if fac == 1:
        return a * b**-1

    return long_division(a, fac)[0] * long_division(b, fac)[0] ** -1


@lru_cache
def extract(poly: Add, var: Var) -> tuple[Node]:
    coeffs = defaultdict(nodes.Const)
    amount = 0
    for term in poly:
        factors = set(nodes.Mul.flatten(term))
        deg = 0
        for i in factors:
            k, v = mult_key(i, 1)
            if k == var:
                factors.remove(i)
                deg = v.numerator
                break

        coeffs[deg] += nodes.Mul.from_terms(factors)
        amount = max(deg, amount)
    return tuple(coeffs.get(idx, nodes.Const(0)) for idx in range(amount, -1, -1))


def rebuild(base: Var, coeffs: tuple[Node]) -> Add | Node:
    return nodes.Add.from_terms(c * base**n for n, c in enumerate(reversed(coeffs)))


@lru_cache
def rational_roots(coeffs: tuple[Node]) -> tuple[tuple[Node]]:
    if len(coeffs) <= 2:
        return (coeffs,)
    q = next(i for i in reversed(coeffs) if i)
    p = coeffs[0]
    if p.__class__ is not nodes.Const:
        p = p.canonical()[0]
    roots = []
    seen = set()
    for q, p in set(product(divisors(q), divisors(p))):
        if len(coeffs) == 1:
            break
        for root in (q / p, -q / p):
            if root in seen:
                continue
            seen.add(root)
            # Extracting root and multiplicity
            while True:
                if len(coeffs) == 1:
                    break
                q, r = synthetic_divide(coeffs, root)
                if r:
                    break
                roots.append((1, -root))
                coeffs = q
    return (*roots, tuple(coeffs))


def factor(node: Node) -> Node:
    if node.__class__ is nodes.Mul:
        return nodes.Mul.from_terms(map(factor, node))
    if node.__class__ is not nodes.Add:
        return node

    if not is_polynomial(node):
        return nodes.Mul.from_terms([node], distr_const=False)

    def pick_best(c, vars):
        tree = defaultdict(int)
        for i in c:
            for j in nodes.Mul.flatten(i, 0):
                k, v = mult_key(j, 1)
                if k not in vars:
                    continue
                tree[k] += v
        # v = min(vars, key=tree.get)
        for v in sorted(vars, key=tree.get):
            res = dfs(extract(c, v), vars - {v})
            if len(res) > 1 or len(res[0]) <= 2:
                return nodes.Mul.from_terms(rebuild(v, i) for i in res)
            # break

    seen = {}

    def dfs(coeffs, vars):
        key = coeffs
        if coeffs in seen:
            return seen[coeffs]
        if vars:
            temp = list(coeffs)
            # recursively factor groups
            for idx, c in enumerate(coeffs):
                if c.__class__ is nodes.Add and (vars_ := {i for i in vars if i in c}):
                    res = pick_best(c, vars_)
                    # Early break
                    if not res:
                        seen[key] = (coeffs,)
                        return seen[key]
                    temp[idx] = res
            coeffs = tuple(temp)
        if not vars:
            sqf = Counter(tuple(i) for i in square_free(coeffs)).items()
            seen[coeffs] = tuple(root for k, v in sqf for root in rational_roots(k) * v)
        else:
            c = gcd(*(i for i in coeffs if i), light=True)
            res = list(rational_roots(tuple(i / c for i in coeffs)))
            if len(res) > 1 or len(coeffs) <= 2:
                if c != 1:
                    res.append((c,))
            else:
                res = (coeffs,)
            seen[coeffs] = tuple(res)
        return seen[coeffs]

    c, node = node.cancel_gcd()
    return nodes.Mul.from_terms(
        [pick_best(node, get_vars(node)) or node, c],
        distr_const=False,
    )


__all__ = [
    "flatten_factors",
    "divisors",
    "gcd",
    "lcm",
    "cancel_factors",
    "extract",
    "rebuild",
    "rational_roots",
    "factor",
]
