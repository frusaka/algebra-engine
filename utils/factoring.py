from __future__ import annotations

from collections import defaultdict
import math
from typing import TYPE_CHECKING

from itertools import chain, product
from functools import lru_cache, reduce
from operator import itemgetter

from datatypes import nodes

from .numeric import primes
from .analysis import mult_key, get_vars
from .polynomial import (
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
        return tuple(primes(expr).items())
    if expr.__class__ is nodes.Pow:
        # return ((expr.base, expr.exp),)
        return tuple((v, exp * expr.exp) for v, exp in flatten_factors(expr.base))
    return ((expr, nodes.Const(1)),)


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


def _gcd_pow(exps, rational):
    exps = tuple(exps)
    if all(isinstance(i, (int, nodes.Number)) for i in exps):
        if rational:
            return min(i // 1 for i in exps)
        return min(exps)
    sybs = dict(
        i.canonical() if not isinstance(i, (nodes.Number, int)) else (i, None)
        for i in exps
    )
    if len(set(sybs.values())) == 1:
        p = min(sybs)
        v = sybs.popitem()[1]
        if rational:
            return p // 1 * v
        return p * v
    raise ValueError(f"unknown value for min{exps}")


def gcd(*args: Node, light=False, rational=True) -> Node:
    """Greatest Common Divisor"""
    args = set(args)
    if len(args) == 0:
        raise ValueError("gcd() requires at least one argument")
    if len(args) == 1:
        return args.pop()
    # Find factor by traversing the node tree
    if light or not all(n.__class__ is nodes.Add and is_polynomial(n) for n in args):
        # Find GCD of symbols and numbers seperately
        nums, symbs = zip(*(i.canonical() for i in args))
        n = [1] * len(nums)
        d = n[:]
        for idx, i in enumerate(nums):
            if i.__class__ is not nodes.Const:
                break
            d[idx] = i.denominator
            if i.numerator.imag:
                if not i.numerator.real:
                    n[idx] = i.numerator.imag
                else:
                    n[idx] = math.gcd(i.numerator.real, i.numerator.imag)
            else:
                n[idx] = i.numerator
        factors = [
            (
                dict(
                    flatten_factors(n)
                    if n.__class__ is not nodes.Add
                    else chain(*map(flatten_factors, n.cancel_gcd()))
                )
                if n
                else {}
            )
            for n in symbs
        ]
        n, d = nodes.Const(math.gcd(*n)), nodes.Const(math.gcd(*d))
        for idx in range(len(nums)):
            factors[idx][n] = 1
            factors[idx][d] = -1
        common = reduce(lambda a, b: a & b, map(dict.keys, factors))
        return nodes.Mul.from_terms(
            t ** _gcd_pow(map(itemgetter(t), factors), rational) for t in common
        )

    # Guaranteed to be working on two or more polynomials
    args = [(n / v, v) for n, v in ((n, gcd(*n.args, light=True)) for n in args)]
    c = gcd(*map(itemgetter(1), args), light=True)
    args = set(map(itemgetter(0), args))
    a = args.pop()
    for b in args:
        if degree(b) > degree(a):
            a, b = b, a
        # Find common factor (Euclidean GCD)
        while b:
            q, r = long_division(a, b)
            if not q or r and r.__class__ is not nodes.Add:
                return c
            a, b = b, r

    return a.cancel_gcd()[1].multiply(c)


def lcm(*args: Node, light=False, rational=True) -> Node:
    """Lowest Common Multiple"""
    args = set(args)  # remove duplicates
    if len(args) == 0:
        raise ValueError("lcm() requires at least one argument")
    if len(args) == 1:
        return args.pop()
    if light or not all(is_polynomial(i) and i.__class__ is nodes.Add for i in args):
        res = args.pop()
        while args:
            b = args.pop()
            res = res * b / gcd(res, b)
        return res
    res = res = args.pop()
    while args:
        b = args.pop()
        res = cancel_factors(res.multiply(b), gcd(res, b))
    return res


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
    if node.__class__ is nodes.Pow:
        return nodes.Pow(factor(node.base), node.exp)
    if node.__class__ is not nodes.Add:
        return node

    if not is_polynomial(node):
        return nodes.Mul.from_terms([node], distr_const=False)

    seen = {}
    vars_dict = {}

    prev = 0

    def next_var(v):
        nonlocal prev
        for i, j in vars_dict.items():
            if j == v:
                return i
        out = 1
        for v in nodes.Mul.flatten(v):
            e = 1
            if v.__class__ is nodes.Pow:
                v, e = v.base, v.exp
            for i, j in vars_dict.items():
                if j == v:
                    res = i
                    break
            else:
                if v.__class__ is nodes.Var:
                    res = v
                else:
                    res = nodes.Var(f"r{prev}")
                    vars_dict[res] = v
                    prev += 1
            out *= res**e
        return out

    def pick_best(c, vars, finalize=False):
        tree = defaultdict(int)
        for i in c:
            for j in nodes.Mul.flatten(i, 0):
                k, v = mult_key(j, 1)
                if k not in vars:
                    continue
                tree[k] += v
        for v in sorted(vars, key=tree.get):
            res = dfs(extract(c, v), vars - {v})
            if not res or any(i.__class__ is nodes.Add for j in res for i in j):
                continue
            res = nodes.Mul.from_terms(rebuild(v, i) for i in res)
            if finalize and vars_dict:
                return res.subs({k: v.subs(vars_dict) for k, v in vars_dict.items()})
            return res

    def dfs(
        coeffs,
        vars,
    ):
        if coeffs in seen:
            return seen[coeffs]
        temp = coeffs
        if vars:
            temp = list(coeffs)
            # recursively factor groups
            for idx, c in enumerate(coeffs):
                if c.__class__ is nodes.Add and (vars_ := {i for i in vars if i in c}):
                    res = pick_best(c, vars_)
                    # Early break
                    if not res:
                        seen[coeffs] = None
                        return seen[coeffs]
                    c, b = res.canonical()
                    temp[idx] = c * next_var(b)
        c = gcd(*(i for i in temp if i))
        temp = tuple(i / c for i in temp)
        n = 0

        sqf_ = square_free(temp)
        sqf = defaultdict(int)
        for i in sqf_:
            if len(i) > 1:
                n += 1
                sqf[i] += 1
            else:
                c *= i[0]
        res = list(root for k, v in sqf.items() for root in rational_roots(k) * v)
        # Hacky: What constitutes af "factored" vs "infactorable"?
        if not (n > 1 or len(res) > 1 or len(res[0]) <= 2):
            res = None
        elif c != 1:
            res.append((c,))
        seen[coeffs] = seen[temp] = res
        return seen[coeffs]

    c, node = node.cancel_gcd()
    node = node.expand()
    return nodes.Mul.from_terms(
        [pick_best(node, get_vars(node), True) or node, c],
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
