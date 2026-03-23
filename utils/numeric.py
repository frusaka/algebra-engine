from __future__ import annotations

from typing import TYPE_CHECKING

from math import gcd
from collections import defaultdict

import datatypes.nodes as nodes


if TYPE_CHECKING:
    from datatypes.nodes import *


def primes(n: Const) -> dict[Const, int]:
    """Get the prime factorization as a dictionary {prime:exponent}"""
    if n.denominator != 1:
        res = primes(nodes.Const(n.numerator))
        den = primes(n.denominator)
        for p, exp in den.items():
            res[p] = -exp
        return res
    if n.numerator.imag:
        if not n.numerator.real:
            return {
                nodes.Const(1j): 1,
                **primes(nodes.Const(n.numerator.imag, n.denominator)),
            }

        if (g := gcd(int(n.numerator.real), int(n.numerator.imag))) > 1:
            return {
                nodes.Const(n.numerator / g): 1,
                **primes(nodes.Const(g, n.denominator)),
            }
        return {n: 1}
    n = n.numerator
    if abs(n) > 1 << 40:
        return {nodes.Const(n): 1}
    was_neg = False
    i = 2
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


def simplify_radical(n: Const, root: int = 2) -> tuple[Const]:
    if n == 0 or n == 1 or root == 1:
        return n, 1, 1

    factors = primes(n)
    # Check if power can be reduced further
    # E.g: 27^(1/6) => (3^3)^(1/6) => 3^(3*1/6) => 3^(1/2)
    cd = gcd(root, *factors.values())

    v = c = nodes.Const(1)
    for prime, exp in factors.items():
        whole, remainder = divmod(exp // cd, root // cd)
        b = prime**remainder
        c *= prime**whole
        if not b.numerator.imag and b < 0:
            if root % 2:
                c *= b
                continue
            if root == 2:
                c *= b * -1j
                continue
        v *= b

    return c, v, nodes.Const(1, root // cd)


__all__ = ["primes", "simplify_radical"]
