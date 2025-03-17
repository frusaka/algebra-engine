from __future__ import annotations
from typing import TYPE_CHECKING

from .bases import Unknown, Atomic
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Variable(Unknown, str, Atomic):
    """An unknown in an experssion"""

    __hash__ = str.__hash__
    __eq__ = str.__eq__

    def __repr__(self) -> str:
        return self

    @dispatch
    def add(b: Proxy[Term], a: Term) -> Term:
        return type(a)(a.coef + b.value.coef, a.value, a.exp)

    @dispatch
    def mul(b: Proxy[Term], a: Term) -> None:
        pass

    @mul.register(variable)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        b = b.value
        if a.like(b, 0):
            if type(a.exp) is not type(b.exp):
                exp = type(a)(value=a.exp) + type(a)(value=b.exp)
            else:
                exp = a.exp + b.exp
            return type(a)(a.coef * b.coef, a.value, exp)

    @mul.register(number)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        if b.value.exp == 1:
            return type(a)(a.coef * b.value.value, a.value, a.exp)

    @mul.register(polynomial | product)
    def _(b: Proxy[Term], a: Term) -> Term | None:
        return b.value.value.mul(Proxy(a), b.value)

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> None:
        # Algebra object has a good enough default fallback for Variable exponentiation
        pass

    pow.register(polynomial)(Atomic.poly_pow)
