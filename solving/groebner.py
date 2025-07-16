from __future__ import annotations
import itertools
import math

from datatypes.base import Node

from datatypes import *
import utils


def leading(f: Add, vars):
    # leading term using lex order
    res = {}
    for i in Add.flatten(f):
        v = i.canonical()[1]
        if v is None:
            res[i] = (0,)
            continue
        k = dict(utils.mult_key(i, 1) for i in Mul.flatten(v, 0))
        res[i] = tuple(k.get(vars[i], 0) for i in range(len(vars)))
    return max(res, key=res.get)


def spolynomial(f: Add, g: Add, vars):
    lt_f = leading(f, vars)
    lt_g = leading(g, vars)
    lcm = utils.lcm(lt_f.canonical()[1] or 1, lt_g.canonical()[1] or 1)
    return g.multiply(lcm / lt_g) - f.multiply(lcm / lt_f)


def reduce(f, G, vars):
    def divide(a, b, vars):
        q = []
        leading_b = leading(b, vars)
        while a:
            if utils.hasremainder(fac := (leading(a, vars) / leading_b)):
                break
            a += b.multiply(-fac)
            q.append(fac)
        return nodes.Add(*q), a

    r = f
    while r:
        divided = False
        for g in G:
            # Try single division step
            q, rem = divide(r, g, vars)
            if q:
                r = rem
                divided = True
                break  # Restart with updated r
        if not divided:
            break
    return r


def buchberger(G: list[Add], vars: list[Var]) -> list[Add | Node]:
    G = G.copy()
    pairs = list(itertools.combinations(range(len(G)), 2))

    while pairs:
        i, j = pairs.pop(0)
        S = spolynomial(G[i], G[j], vars)
        R = reduce(S, G, vars)
        if R:
            # Inconsistent?
            if R.__class__ is Const:
                return []
            G.append(R)
            new_idx = len(G) - 1
            for k in range(new_idx):
                pairs.append((k, new_idx))

    reduced = []
    for i, f in enumerate(G):
        r = reduce(f, reduced, vars)
        if not r:
            continue
        if r.__class__ is Add:
            if (d := math.lcm(*(i.canonical()[0].denominator for i in r))) > 1:
                r = r.multiply(d)
            if (g := math.gcd(*(i.canonical()[0].numerator for i in r))) > 1:
                r = r.multiply(Const(1, g))
            reduced.append(r)
        else:
            reduced.append(r.as_ratio()[0])
    return reduced


__all__ = ["buchberger"]
