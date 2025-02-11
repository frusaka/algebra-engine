from __future__ import annotations
from functools import cache
import math
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from data_types import Term, Number, Collection, Comparison, Variable


@cache
def lexicographic_weight(term: Term, alphabetic=True) -> Number:
    from data_types import Number, Variable, Collection

    if not isinstance(term.exp, Number) or (
        isinstance(term.value, Number) and term.exp == 1
    ):
        return Number(0)
    res = Number(0)

    if isinstance(term.value, Collection) and term.exp == 1:
        if alphabetic and term.fractional.value:
            return res - 10000
        # Calling sum() does not work
        seen = {}
        for t in term.value:
            if not isinstance(t.exp, Number):
                continue
            seen[t.value] = max(
                lexicographic_weight(t, alphabetic), seen.get(t.value, res)
            )
        for i in seen.values():
            res += i

        return res
    res = term.exp
    if isinstance(term.value, Variable) and alphabetic:
        # Map range formula
        a, b = ord("A"), ord("z")
        c, d = 0, 0.1
        x = ord(term.value)
        res += c + ((x - a) * (d - c)) / (b - a)
    if isinstance(term.value, Number):
        return -res
    return res


def standard_form(collection: Sequence[Term]) -> list[Collection]:
    return sorted(collection, key=lexicographic_weight, reverse=1)


def quadratic(comp: Comparison, var: Variable) -> tuple[Term] | None:
    """
    Given that the lhs is a Polynomial,
    check whether it can be considered quadratic in terms of `value` and return a tuple (a, b, c)
    """
    from data_types import Term

    a, b = None, None
    x = Term(value=var)
    for t in comp.left.value:  # Must be a Polynomial
        v = t / x
        # Checks to detect a Quadratice
        # One term that when divided by x cancels the x
        if var not in v:
            if b:
                return
            b = v
            bx = t
        # One term that when divided by x^2 cancels the x
        elif var not in (v := v / x):
            if a:
                return
            a = v
            ax_2 = t
        # Should otherwise not contain x if not divisible by x or x^2
        elif var in t:
            return
    # Not a quadratic
    # For values like x^2-9=0, they can be solved without the quadratic formula
    if not a or not b:
        return
    # Make the rhs 0
    if comp.right.value:
        comp = comp.reverse_sub(comp.right)
        print(comp)
    # The rest of the boys, can even be another Polynomial
    c = comp.left - (ax_2 + bx)
    return a, b, c


def quadratic_formula(a: Term, b: Term, c: Term) -> Term:
    """Apply the quadratic formula: (-b ± (b^2 - 4ac))/2a"""
    from data_types import Term, Number, Solutions

    print(
        f"q(a={a}, b={b}, c={c})",
        "(-b ± 2√(b^2 - 4ac))/2a",
        sep=" = ",
    )
    rhs = (b ** Term(Number(2)) - Term(Number(4)) * a * c) ** Term(Number("1/2"))
    den = Term(Number(2)) * a
    res = {(-b + rhs) / den, (-b - rhs) / den}
    if len(res) == 1:
        return res.pop()
    return Solutions(res)


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
    from data_types import Term, Number

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
