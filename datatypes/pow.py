from __future__ import annotations

from dataclasses import dataclass
import itertools
import functools
from typing import TYPE_CHECKING

import utils

from . import expr
from .base import Collection, Expr


@dataclass(frozen=True, init=False, slots=True)
class Pow(Expr):
    base: Expr
    exp: Expr

    @utils.lru_cache
    def __new__(cls, base: Expr, exp: Expr) -> Expr:
        if base == 1:
            return base
        if base.__class__ is Pow:
            # May nullify constraints: √(x-2)^2 = |x-2|, not x-2
            base, exp = base.base, exp * base.exp
        if exp == 0:
            return expr.Const(1)
        if exp == 1:
            return base
        c = 1
        if exp.__class__ is expr.Const:
            if base.__class__ is expr.Mul:
                return expr.Mul.from_terms(
                    (t**exp for t in base.args), distr_const=True
                )
            if isinstance(base, expr.Number):
                if base.__class__ is expr.Float:
                    return base.pow(exp)
                if exp.denominator == 1:
                    return base.pow(exp.numerator)
                c, base, exp = utils.simplify_radical(
                    base.pow(exp.numerator), exp.denominator
                )
                if base == 1 or exp == 1:
                    return c
            elif base.__class__ is expr.Add:
                c, base = base.cancel_gcd(normalize=exp < 0)
                c **= exp
        self = super(Pow, cls).__new__(cls)
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "exp", exp)
        if c != 1:
            return expr.Mul(self, c)
        return self

    if TYPE_CHECKING:

        def __init__(self, base: Expr, exp: Expr) -> None:
            pass

    def __repr__(self) -> str:
        base = str(self.base)
        if (
            isinstance(self.base, Collection)
            or self.base.__class__ is expr.Const
            and self.base.denominator > 1
        ):
            base = base.join("()")
        if self.exp.__class__ is expr.Const:
            p = utils.superscript(self.exp.numerator) if self.exp.numerator != 1 else ""
            base += p
            if self.exp.denominator != 1:
                r = (
                    utils.superscript(self.exp.denominator)
                    if self.exp.denominator != 2
                    else ""
                )
                base = r + "√" + base
            return base

        exp = str(self.exp)
        if isinstance(self.exp, Collection):
            exp = exp.join("()")
        return f"{base}^{exp}"

    def as_ratio(self) -> tuple[Expr]:
        if self.exp.canonical()[0].is_neg():
            return (expr.Const(1), Pow(self.base, -self.exp))
        return (self, expr.Const(1))

    def _simplify(self) -> Expr:
        return Pow(self.base.factor(), self.exp.factor())

    def _expand(self) -> Expr:
        if self.exp.canonical()[0].is_neg():
            return Pow(Pow(self.base, -self.exp)._expand(), expr.Const(-1))
        base = self.base._expand()
        exp = self.exp._expand()
        if (
            base.__class__ is expr.Add
            and exp.__class__ is expr.Const
            and not exp.numerator.imag
            and exp.numerator > 1
        ):
            base = functools.reduce(
                Expr.multiply, itertools.repeat(base, exp.numerator)
            )
            if exp.denominator == 1:
                return base
            exp = expr.Const(1, exp.denominator)
        return Pow(base, exp)

    def _approx(self) -> float | complex:
        v = self.base._approx()
        e = self.exp._approx()
        if (
            self.exp.__class__ is expr.Const
            and self.exp.denominator % 2
            and self.exp.denominator > 1
            and not v.imag
            and v < 0
        ):
            return -abs(v) ** e
        return v**e

    def totex(self) -> str:
        from .mul import _tex

        if not isinstance(self.exp, expr.Const) or self.exp.denominator == 1:
            base = _tex(self.base).join("{}")
            exp = self.exp.totex().join("{}")
            return f"{base}^{exp}"
        base = self.base.totex()
        if self.exp.numerator != 1:
            base = _tex(self.base) + "^" + str(self.exp.numerator).join("{}")
        base = base.join("{}")
        r = self.exp.denominator
        if r == 2:
            return f"\\sqrt{base}"
        return f"\\sqrt[{r}]{base}"


__all__ = ["Pow"]
