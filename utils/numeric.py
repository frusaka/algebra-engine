from __future__ import annotations

from typing import TYPE_CHECKING

from math import gcd
from collections import defaultdict
from . import expr

if TYPE_CHECKING:
    from datatypes.expr import *


def primes(n: Const) -> dict[Const, int]:
    """Get the prime factorization as a dictionary {prime:exponent}"""
    if n.denominator != 1:
        res = primes(expr.Const(n.numerator))
        den = primes(n.denominator)
        for p, exp in den.items():
            res[p] = -exp
        return res
    if n.numerator.imag:
        if not n.numerator.real:
            return {
                expr.Const(1j): 1,
                **primes(expr.Const(n.numerator.imag, n.denominator)),
            }

        if (g := gcd(n.numerator.real, n.numerator.imag)) > 1:
            return {
                expr.Const(n.numerator / g): 1,
                **primes(expr.Const(g, n.denominator)),
            }
        return {n: 1}
    n = n.numerator
    if abs(n) > 1 << 40:
        return {expr.Const(n): 1}
    was_neg = False
    i = 2
    if n < 0:
        n = -n
        was_neg = True

    factors = defaultdict(int)
    while i * i <= n:
        while n % i == 0:
            factors[expr.Const(i)] += 1
            n //= i
        i += 1
    if was_neg:
        factors[expr.Const(-1)] = 1
    if n > 1:
        factors[expr.Const(n)] += 1
    return factors


def simplify_radical(n: Const, root: int = 2) -> tuple[Const]:
    if n == 0 or n == 1 or root == 1:
        return n, 1, 1

    factors = primes(n)
    # Check if power can be reduced further
    # E.g: 27^(1/6) => (3^3)^(1/6) => 3^(3*1/6) => 3^(1/2)
    cd = gcd(root, *factors.values())

    v = c = expr.Const(1)
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

    return c, v, expr.Const(1, root // cd)


__all__ = ["primes", "simplify_radical"]
