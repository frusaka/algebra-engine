from __future__ import annotations
import itertools

from datatypes.base import Expr

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
    lcm = utils.lcm(lt_f, lt_g)
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
        return q, a

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
    return r.as_ratio()[0]


def buchberger(G: list[Add], vars: list[Var]) -> list[Add | Expr]:
    # print(G)
    G = [g.expand().as_ratio()[0] for g in G]  # G.copy()
    pairs = list(itertools.combinations(G, 2))
    # idx = 1
    while pairs:
        f, g = pairs.pop(0)
        # idx += 1
        if utils.get_vars(f).isdisjoint(utils.get_vars(g)):
            continue
        # print(f"index {idx}: ({f}, {g}), remaining: {len(pairs)}, G: {len(G)}")
        # print("Reducing: ")
        h = reduce(spolynomial(f, g, vars), G, vars)
        # print(f"Done! {h}")
        if not h:
            continue
        # Inconsistent?
        if h.__class__ is Const:
            return []
        pairs.extend((h, g) for g in G)
        G.append(h)
    # print(G)
    minimal = []
    for g in G:
        if r := reduce(g, minimal, vars):
            minimal.append(r)
    return [
        r for f in minimal if (r := reduce(f, [g for g in minimal if g is not f], vars))
    ]
    print("Groebner:", res)
    return res


__all__ = ["buchberger"]
