from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datatypes import Term


def primes(n: int) -> dict[int]:
    """Get the prime factorization as a dictionary {prime:exponent}"""
    i = 2
    factors = {}
    i = 2
    while i * i <= n:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
        i += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def simplify_radical(n: int, root: int = 2) -> Term:
    from datatypes import Term, Number

    if n == 0:
        return Term(value=Number(0))
    if n < 0:
        # Handle imaginary numbers for even roots
        if root % 2 == 0:
            return simplify_radical(-n, root).scale(Number(complex(imag=1)))
        else:
            return -simplify_radical(-n, root)

    factors = primes(n)

    # **Detect if further simplification is possible**
    cd = math.gcd(root, sum(factors.values()))
    if cd > 1 and cd != root:
        return simplify_radical(round(n ** (1 / cd)), root // cd)

    c = 1  # Extracted part; coeffiecient
    v = 1  # Remains under radical; value

    for prime, exp in factors.items():
        whole, remainder = divmod(exp, root)
        c *= prime**whole
        v *= prime**remainder

    return Term(Number(c), Number(v), exp=Number(1, root))
