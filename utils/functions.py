from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datatypes import Term, Number


def primes(n: Number) -> dict[int]:
    """Get the prime factorization as a dictionary {prime:exponent}"""
    if n.denominator != 1:
        res = primes(n.numerator)
        den = primes(n.denominator)
        for p, exp in den.items():
            res[p] = -exp
        return res
    i = 2
    n = n.numerator
    factors = {}
    while i * i <= n:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
        i += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def simplify_radical(n: Number, root: int = 2, scale: Number = 1) -> Term:
    from datatypes import Term, Number

    if n == 0 or root == 1:
        return Term(value=n * scale)
    if scale.__class__ is not Number:
        scale = Number(scale)
    if n.numerator.imag:
        if not n.numerator.real:
            res = simplify_radical(Number(n.numerator.imag), root, scale)
            if res.exp.denominator == root:
                return Term(
                    res.coef,
                    res.value * Number(1j),
                    Number(1, root),
                )
        return Term(scale, n, Number(1, root))
    if n < 0:
        n *= -1
        scale *= -1 if root % 2 else Number(1j)
    factors = primes(n)
    v = c = Number(1)
    # Check if power can be reduced further
    # E.g: 27^(1/6) => (3^3)^(1/6) => 3^(3*1/6) => 3^(1/2)
    if factors and (cd := math.gcd(root, *factors.values())) > 1:
        root //= cd
        if root == 1:
            c, v = v, c
        for i in factors:
            factors[i] //= cd
    for prime, exp in factors.items():
        whole, remainder = divmod(exp, root)
        prime = Number(prime)
        c *= prime**whole
        v *= prime**remainder
    c *= scale
    return Term(c, v, Number(1, root))
