from __future__ import annotations


import math
import operator
from dataclasses import dataclass
from functools import lru_cache
from enum import Enum

from .solutions import *
from .system import System
from .eval_trace import *

# from datatypes import nodes
from datatypes.base import Collection, Node
from datatypes.nodes import *

import utils
from .utils import difficulty_weight, nth_roots, roots


def rewrite_radicals(expr, value):
    from .system import compute_grobner

    system = []
    counter = []
    cache = {}

    def vars():
        alphabet = [chr(i) for i in range(ord("a"), ord("z") + 1)]
        start_index = alphabet.index(value.lower())
        i = 0
        while True:
            yield Var(alphabet[(start_index + i + 1) % 26])
            i += 1

    def visit(node):
        if node in cache:
            return cache[node]

        if node.__class__ is Pow and value in node:
            sub = visit(node.base) ** node.exp.numerator
            if node.exp.denominator != 1:
                var = next(vars)
                cache[node] = var
                counter.append(var)
                system.append(Comparison(var**node.exp.denominator, sub))
                return var
            cache[node] = sub
            return sub

        elif isinstance(node, Collection):
            return node.from_terms(map(visit, node.args))
        return node

    vars = vars()
    final_expr = visit(expr)
    if not system:
        return

    def key(t):
        v = difficulty_weight(t.left, value)
        return (bool(v[1]), *v)

    system.append(Comparison(final_expr, Const(0)))
    return min(compute_grobner(system, counter + [value], False), key=key)


def simple_isolate_radical(comp, value):
    rad = None
    success = True

    def col():
        nonlocal success, rad
        for t in Add.flatten(comp.left):
            # fmt: off
            if (k:=math.lcm(*(i.exp.denominator for i in Mul.flatten(t,0) if i.__class__ is Pow and value in i)))!=1:
            # fmt: on
                if rad is not None:
                    rad = None
                    return
                rad = (t, k)

    idx = 0
    while True:
        col()
        if not rad:
            break
        if idx:
            ETSteps.register(ETNode(comp))
        t, k = rad
        if comp.left.__class__ is Add:
            comp -= Add(*comp.left.args - {t})
            ETSteps.register(ETNode(comp))
        comp **= k
        rad = None
        idx = 1
    return comp, idx


class CompRel(Enum):
    EQ = 0
    NE = 0.5
    LT = 1
    GT = 2
    LE = 3
    GE = 4
    IN = 5

    def reverse(self):
        if self.value < 1:
            return self
        if self.name.startswith("L"):
            return getattr(CompRel, self.name.replace("L", "G"))
        return getattr(CompRel, self.name.replace("G", "L"))

    def __str__(self):
        return utils.SYMBOLS.get(self.name)

    def totex(self, align: bool = True):
        align = "&" * align
        if self.name.endswith("E") or self.name == "IN":
            return align + f"\\{self.name.lower()}"
        return align + utils.SYMBOLS.get(self.name)


@dataclass(frozen=True, slots=True)
class Comparison:
    left: Node
    right: Node
    rel: CompRel = CompRel.EQ

    def __repr__(self) -> str:
        return "{0} {2} {1}".format(self.left, self.right, self.rel)

    def is_close(self, threshold: float = 1e-7) -> bool:
        v = (self.left - self.right).approx()
        if self.rel is not CompRel.EQ:
            return bool(Comparison(v, 0, self.rel))
        return abs(v) <= threshold

    @lru_cache
    def solve_for(self, value: Var) -> Comparison:
        ETSteps.register(ETNode(self))
        # Rewrite the comparison to put the target variable on the left
        if value in self.right and not value in self.left:
            self = self.reverse()
            ETSteps.register(ETNode(self))
        # Moving target terms to the left
        self = self.collect(value)
        if value not in self:
            return self
        # Isolation by division
        if self.left.__class__ is Mul:
            remove = []
            for t in self.left:
                if (not value in t) or utils.hasremainder(t):
                    remove.append(t)
            if remove:
                return (self / Mul(*remove)).solve_for(value)
            # Zero Product Property
            if self.right == 0:
                return System(
                    Comparison(lhs, self.right) for lhs in self.left
                ).solve_for(value)

        res = self.handle_exponents(value)
        if res != self:
            return res.solve_for(value)

        if res.left == value and value not in res.right:
            return res
        self = res
        # Move undesired terms to the rhs
        if (
            self.left.__class__ is Add
            and len(
                set(
                    utils.degree(i, value) for i in Add.flatten(self.left) if value in i
                )
            )
            == 1
        ):
            if remove := [i for i in self.left if value not in i]:
                return (self - Add.from_terms(remove)).solve_for(value)
            # Try simplifying or expanding
            for t in (self.left.simplify(), self.left.expand()):
                if t != self.left:
                    return Comparison(t, self.right, self.rel).solve_for(value)
        # Normalize
        if self.right:
            self -= self.right
            ETSteps.register(ETNode(self))

        if (eqn := self.expand()) != self:
            return eqn.solve_for(value)
        if (eqn := self.try_factor()) is not None:
            return eqn.solve_for(value)

        return self.get_roots(value)
        # Solving using the quadratic formula
        if (v := self.try_quadratic(value)) is not None:
            return v
        # Try approximations at last
        return self.try_approximate(value)

    def __contains__(self, value: Var) -> bool:
        return value in self.left or value in self.right

    def __sub__(self, value: Node) -> Comparison:
        pad = len(str(self.left)) + 1
        if not value.canonical()[0].is_neg():
            ETSteps.register(ETOperatorNode(ETOperatorType.SUB, value, pad))
        else:
            ETSteps.register(ETOperatorNode(ETOperatorType.ADD, -value, pad))
        return Comparison(self.left - value, self.right - value, self.rel)

    def __truediv__(self, value: Node) -> Comparison:
        pad = len(str(self.left)) + 1
        if value.as_ratio()[1] == 1:
            ETSteps.register(ETOperatorNode(ETOperatorType.DIV, value, pad))
        else:
            ETSteps.register(ETOperatorNode(ETOperatorType.TIMES, value**-1, pad))
        # Used set expression to cancel Floating-Point factors
        return Comparison(
            Mul(*self.left.args ^ set(Mul.flatten(value))),
            self.right / value,
            self.reverse_sign(value),
        )

    def __pow__(self, value: Const) -> Comparison:
        pad = len(str(self.left)) + 1
        if value.denominator != 1 and value.numerator == 1:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.SQRT, value.denominator, pad)
            )
        else:
            ETSteps.register(ETOperatorNode(ETOperatorType.POW, value, pad))
        lhs = self.left**value
        if value.denominator > 1:
            rhs = nth_roots({self.right}, value.denominator)
            if len(rhs) > 1:
                return System(Comparison(lhs, r) for r in rhs)
            rhs = rhs.pop()
        else:
            rhs = self.right**value
        return Comparison(lhs, rhs, self.rel)

    def __bool__(self) -> bool:
        return getattr(operator, self.rel.name.lower())(self.left, self.right)

    def collect(self, value: Var) -> Comparison:
        remove = []
        for t in Add.flatten(self.right):
            if value in t:
                remove.append(t)
        if remove:
            self -= Add.from_terms(remove, 0)
            ETSteps.register(ETNode(self))
        return self

    def handle_exponents(self, value: Var) -> Comparison:
        self, changed = simple_isolate_radical(self, value)
        rad = rewrite_radicals(self.left - self.right, value)
        if rad is not None:
            if changed:
                ETSteps.register(ETNode(self))
            return rad
        if (
            exp := math.gcd(
                *(
                    utils.mult_key(i, 1)[1].numerator
                    for i in Mul.flatten(self.left, 0)
                    if value in i
                )
            )
        ) > 1 and value not in self.right:
            if changed:
                ETSteps.register(ETNode(self))
            return self ** Const(1, exp)
        return self

    def try_factor(self) -> Comparison | None:
        if (
            utils.is_polynomial(self.left)
            and (f := (self.left).simplify()).__class__ is not Add
        ):
            # ETSteps.register(ETTextNode("Simplified Expression"))
            return Comparison(f, Const(0), self.rel)

    def get_roots(self, value: Var) -> Comparison | System:
        f = utils.extract(self.left.expand(), value)
        Z = roots(f)

        if len(Z) == 1:
            r = Comparison(value, Z.pop())
            ETSteps.register(ETNode(r))
        else:
            r = System(Comparison(value, root) for root in Z)
            ETSteps.register(ETBranchNode(r))
        return r

    def reverse(self) -> Comparison:
        """Write the comparison in reverse"""
        return Comparison(self.right, self.left, self.rel.reverse())

    def normalize(self) -> Comparison:
        """Put all terms on the lhs"""
        return Comparison(self.left - self.right, Const(), self.rel)

    def reverse_sign(self, value: Node) -> CompRel:
        # Can safely flip sign based on coefficient:
        # operators.solve() will gracefully handle any mishaps
        if self.rel in {CompRel.EQ, CompRel.NE}:
            return self.rel
        value = value.canonical()[0]
        if value < 0:
            return self.rel.reverse()
        return self.rel

    def subs(self, mapping: dict) -> Comparison:
        return Comparison(self.left.subs(mapping), self.right.subs(mapping), self.rel)

    def simplify(self):
        return Comparison(self.left.simplify(), self.right.simplify(), self.rel)

    def expand(self):
        return Comparison(self.left.expand(), self.right.expand(), self.rel)

    def totex(self, align: bool = True) -> str:
        left, rel, right = self.left, self.rel, self.right
        if self.right.__class__ is Collection:
            rel = "&" * align + "\\in"
        else:
            rel = rel.totex(align)
        if left.__class__ is tuple:
            left = ",".join(left).join(("\\left(", "\\right)"))
        else:
            left = left.totex()
        if right.__class__ is tuple:
            right = ",".join(map(lambda x: x.totex(), right)).join(
                ("\\left(", "\\right)")
            )
        else:
            right = right.totex()
        return "{0}{2}{1}".format(left, right, rel)


__all__ = ["CompRel", "Comparison"]
