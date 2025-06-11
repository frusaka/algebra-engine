from __future__ import annotations
from typing import TYPE_CHECKING

from .bases import Atomic
from utils import *

if TYPE_CHECKING:
    from .term import Term


class Variable(str, Atomic):
    """An unknown in an experssion"""

    def __repr__(self) -> str:
        return self

    @dispatch
    def add(b: Proxy[Term], a: Term) -> Term:
        return type(a)(a.coef + b.value.coef, a.value, a.exp)

    @dispatch
    def mul(b: Proxy[Term], a: Term) -> Term | None:
        return b.value.value.mul(Proxy(a), b.value)

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

    @dispatch
    def pow(b: Proxy[Term], a: Term) -> None:
        # Term class has a good enough default fallback for Variable exponentiation
        pass

    def ast_subs(self, mapping: dict):
        return mapping.get(self, self)

    def totex(self):
        return self
