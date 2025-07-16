from __future__ import annotations

from typing import TYPE_CHECKING

import math
from collections import defaultdict

import datatypes.nodes as nodes


if TYPE_CHECKING:
    from datatypes.nodes import *
    from datatypes.base import Node


def primes(n: Const) -> dict[Const, int]:
    """Get the prime factorization as a dictionary {prime:exponent}"""
    if n.denominator != 1:
        res = primes(n.numerator)
        den = primes(n.denominator)
        for p, exp in den.items():
            res[p] = -exp
        return res
    if abs(n) > 1 << 40:
        return {n: 1}
    i = 2
    was_neg = False
    n = n.numerator
    if n < 0:
        n = -n
        was_neg = True

    factors = defaultdict(int)
    while i * i <= n:
        while n % i == 0:
            factors[nodes.Const(i)] += 1
            n //= i
        i += 1
    if was_neg:
        factors[nodes.Const(-1)] = 1
    if n > 1:
        factors[nodes.Const(n)] += 1
    return factors


def simplify_radical(n: Const, root: int = 2, scale: Const = 1) -> tuple[Node]:
    if n == 0 or root == 1:
        return n, 1, 1
    if n.numerator.imag:
        if not n.numerator.real:
            c, v, exp = simplify_radical(nodes.Const(n.numerator.imag), root, scale)
            if exp.denominator == root:
                return c * scale, v * 1j, nodes.Const(1, root)
        return scale, n, nodes.Const(1, root)
    if n < 0:
        n *= -1
        if root % 2:
            scale *= -1
        elif root == 2:
            scale *= 1j
        else:
            c, v, exp = simplify_radical(n, root, scale)
            if exp.denominator == root:
                return c, -v, exp
            if exp.denominator == 1:
                return c, -v, nodes.Const(1, root)
            return scale, -n, nodes.Const(1, root)
    factors = primes(n)
    v = c = nodes.Const(1)
    # Check if power can be reduced further
    # E.g: 27^(1/6) => (3^3)^(1/6) => 3^(3*1/6) => 3^(1/2)
    if factors and (cd := math.gcd(root, *factors.values())) > 1:
        root //= cd
        for i in factors:
            factors[i] //= cd

    for prime, exp in factors.items():
        whole, remainder = divmod(exp, root)
        c *= prime**whole
        v *= prime**remainder
    c *= scale
    return c, v, nodes.Const(1, root)


__all__ = ["primes", "simplify_radical"]
