from __future__ import annotations

import math
from typing import TYPE_CHECKING
from functools import lru_cache

from datatypes import nodes
from .analysis import order_key

if TYPE_CHECKING:
    from datatypes.base import Node
    from datatypes.nodes import *


def is_polynomial(node: Node) -> bool:
    """Checks whether a node is a valid term to be considered or be inside a Add"""
    match node.__class__.__name__:
        case "Const" | "Var":
            return True
        case "Pow":
            if node.exp.__class__ is not nodes.Const or node.exp.denominator != 1:
                return False
            return is_polynomial(node.base)
        case "Mul" | "Add":
            return all(map(is_polynomial, node.args))
    return False


@lru_cache
def degree(node: Node) -> int | None:
    match node.__class__.__name__:
        case "Const":
            return 0
        case "Var":
            return 1
        case "Pow":
            if node.exp.__class__ is not nodes.Const or node.exp.denominator != 1:
                return
            return degree(node.base) * node.exp.numerator
        case "Mul":
            return sum(map(degree, node.args))
        case "Add":
            return max(map(degree, node.args))
    raise TypeError("Unsupported type for degree", node, type(node))


def leading(node: Node) -> Node:
    if node.__class__ is nodes.Add:
        return max(node, key=order_key)
    return node


def leading_options(node: Add) -> Node:
    lead = leading(node)
    return (i for i in node.args if degree(i) == degree(lead))


def hasremainder(node: Node):
    if node.__class__ is nodes.Pow:
        return node.exp.canonical()[0] < 0
    if node.__class__ is not nodes.Mul:
        return False
    for i in node.args:
        if i.__class__ is not nodes.Pow:
            continue
        if i.exp.canonical()[0] < 0:
            return True
    return False


def long_division(a: Add, b: Node) -> tuple[list[Node], Node]:
    """
    Backend long division algorithm. `a` must have a higher degree than `b`.
    Returns Q -> Quotient, r -> remainder
    """

    org, q = a, []
    leading_b = leading(b)
    while a.__class__ is nodes.Add and degree(a) >= degree(b):
        for leading_a in leading_options(a):
            if not hasremainder(fac := (leading_a / leading_b)):
                break
        else:
            if degree(leading_a) > degree(leading_b):
                q = []
                a = org
            break
        a += b.multiply(-fac)
        q.append(fac)
    # if type(a) is nodes.Const and a != 0:
    #     q = [i / a for i in q]
    #     a -= a
    return q, a


def synthetic_divide(coeffs: list[Node], r: Node) -> tuple[list[Node], Node]:
    """Divide poly by (x - r): returns (quotient_coeffs, remainder)"""
    q = [coeffs[0]]  # bring down the leading coefficient
    for i in range(1, len(coeffs)):
        q.append(q[-1] * r + coeffs[i])
    return q[:-1], q[-1]  # last is remainder


@lru_cache
def poly_divide(dividend, divisor):
    """Divide dividend by divisor: both are lists of coefficients (high to low degree)."""
    deg_dividend = len(dividend) - 1
    deg_divisor = len(divisor) - 1

    if deg_dividend < deg_divisor:
        return (0,), dividend  # quotient 0, remainder is dividend

    dividend = list(dividend)
    divisor = list(divisor)

    quotient = [0] * (deg_dividend - deg_divisor + 1)
    remainder = dividend[:]
    for i in range(len(quotient)):
        lead_coeff = remainder[i] / divisor[0]
        if hasremainder(lead_coeff):
            raise ValueError("Expected list of coefficients")
        quotient[i] = lead_coeff

        # Subtract lead_coeff * (divisor shifted)

        for j in range(len(divisor)):
            remainder[i + j] -= lead_coeff * divisor[j]
    # Trim leading zeroes
    while remainder and remainder[0] == 0:
        remainder.pop(0)

    return tuple(quotient), tuple(remainder)


@lru_cache
def derivative(poly: tuple[Node]) -> tuple[Node]:
    m = len(poly) - 1
    return tuple((m - n) * poly[n] for n in range(m))


@lru_cache
def square_free(poly: tuple[Const]) -> tuple:
    if len(poly) <= 2:
        return normalize(poly)

    prime = derivative(poly)
    g = poly_gcd(poly, prime)

    if len(g) == 1:
        return normalize(poly)

    w = tuple(poly_divide(poly, g)[0])
    g = tuple(g)
    return (*square_free(w), *square_free(g))


def normalize(a):
    # Normalizing the gcd
    if (d := math.lcm(*(i.denominator for i in a if i))) != 1:
        a = [i * d for i in a]
    g = -1 if a[0] < 0 else 1
    g *= math.gcd(*(i.numerator for i in a if i))
    if g != 1:
        a = [i / g for i in a]
    return tuple(a), (nodes.Const(g, d),)


@lru_cache
def poly_gcd(a, b):
    if len(b) > len(a):
        a, b = b, a
    # Find common factor (Euclidean GCD)
    while b:
        q, r = poly_divide(a, b)
        if not q or r and len(r) == 1:
            return (1,)
        a, b = b, r
    return a


__all__ = [
    "is_polynomial",
    "degree",
    "leading",
    "leading_options",
    "hasremainder",
    "derivative",
    "poly_gcd",
    "square_free",
    "long_division",
    "synthetic_divide",
    "poly_divide",
]
