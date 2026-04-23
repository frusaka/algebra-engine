from __future__ import annotations

from copy import copy
import math
import operator
from dataclasses import dataclass
from enum import Enum

from .solutions import *
from .system import System

# from datatypes import nodes
from datatypes.base import Collection, Node
from datatypes.nodes import *
from utils.steps import *
from utils import steps

import utils
from .utils import difficulty_weight, nth_roots, roots, compute_grobner


def rewrite_radicals(expr, value):

    system = []
    counter = []
    cache = {}

    def vars():
        i = 0
        while True:
            yield Var(f"r{i}")
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
            steps.register(comp)
        t, k = rad
        if comp.left.__class__ is Add:
            comp -= Add(*set(comp.left.args) - {t})
            steps.register(comp)
        comp **= k
        rad = None
        idx = 1
    return comp


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


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Comparison:
    left: Node
    right: Node
    rel: CompRel = CompRel.EQ

    def __post_init__(self):
        steps.register(
            Step(
                "",
                ETOperator(self.rel.name, (self.left, self.right), self),
            ),
            False,
        )

    def __repr__(self) -> str:
        return "{0} {2} {1}".format(self.left, self.right, self.rel)

    # @steps.tracked("approximate")
    def is_close(self, threshold: float = 1e-7) -> bool:
        v = (self.left - self.right).approx()
        if self.rel is not CompRel.EQ:
            res = bool(Comparison(v, 0, self.rel))
        else:
            res = abs(v) <= threshold
        steps.register(v)
        steps.register(Step("", ETOperator(self.rel.name, (v, 0), res)))
        return res

    def solve_for(self, value: Var) -> Comparison:
        org = self
        while True:
            ## If input expression was simplified, double steps.register
            if self is not org:
                steps.register(self)
            if self.__class__ is not Comparison:
                return self.solve_for(value)
            # Rewrite the comparison to put the target variable on the left
            if value in self.right and not value in self.left:
                self = self.reverse()  # .solve_for(value)
                continue
            # Moving target terms to the left
            res = self.collect(value)
            if value not in res:
                return res
            if res != self:
                self = res
                continue
            # Isolation by division
            if self.left.__class__ is Mul:
                remove = []
                for t in self.left:
                    if (not value in t) or utils.hasremainder(t):
                        remove.append(t)
                if remove:
                    self = self / Mul(*remove, distr_const=True)  # .solve_for(value)
                    continue
                # Zero Product Property
                if self.right == 0:
                    res = self.zpp()
                    steps.register(res)
                    return res.solve_for(value)

            res = self.handle_exponents(value)
            if res != self:
                self = res
                continue
            if res.left == value and value not in res.right:
                return res
            self = res
            # Move undesired terms to the rhs
            if (
                self.left.__class__ is Add
                and len(
                    set(
                        utils.degree(i, value)
                        for i in Add.flatten(self.left)
                        if value in i
                    )
                )
                == 1
            ):
                if remove := [i for i in self.left if value not in i]:
                    self = self - Add.from_terms(remove)  # .solve_for(value)
                    continue
                # Try simplifying or expanding
                if (eqn := self.factor(True)) != self:
                    self = eqn
                    continue

            # Normalize
            if self.right:
                self -= self.right
                steps.register(self)
            if (eqn := self.expand()) != self:
                self = eqn
                continue
            if (eqn := self.factor()) != self:
                self = eqn
                continue
            if (eqn := self.get_roots(value)) != self:
                self = eqn
                continue
            break

    def __contains__(self, value: Var) -> bool:
        return value in self.left or value in self.right

    @steps.tracked("SUB", "Subtract from both sides")
    def __sub__(self, value: Node) -> Comparison:
        lhs, rhs = self.left - value, self.right - value
        steps.register(lhs)
        steps.register(rhs)
        return Comparison(lhs, rhs, self.rel)

    @steps.tracked("DIV", "Divide both sides")
    def __truediv__(self, value: Node) -> Comparison:
        lhs, rhs = self.left / value, self.right / value
        steps.register(lhs)
        steps.register(rhs)
        if type(lhs) is Mul and lhs.args[0] == 1:
            lhs = Mul(*lhs.args[0:])
        return Comparison(lhs, rhs, self.reverse_sign(value))

    @steps.tracked("POW", "Raise both sides")
    def __pow__(self, value: Const) -> Comparison:
        lhs = self.left**value
        if value.denominator > 1:
            rhs = nth_roots({self.right}, value.denominator)
            if len(rhs) > 1:
                steps.register(lhs)
                steps.register(
                    Step(
                        "Root",
                        ETOperator(
                            "SQRT", (self.right, value.denominator), ETBranch(rhs)
                        ),
                    )
                )
                return System(Comparison(lhs, r) for r in rhs)
            rhs = rhs.pop()
        else:
            rhs = self.right**value
        steps.register(lhs)
        steps.register(rhs)
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
        return self

    def handle_exponents(self, value: Var) -> Comparison:
        self = simple_isolate_radical(self, value)
        rad = rewrite_radicals(self.left - self.right, value)
        if rad is not None:
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
            return self ** Const(1, exp)
        return self

    @steps.tracked("roots", "Find roots")
    def get_roots(self, value: Var) -> Comparison | System:
        f = utils.extract(self.left.expand(), value)
        Z = roots(f)

        if len(Z) == 1:
            r = Comparison(value, Z.pop())
        else:
            r = System(Comparison(value, root) for root in Z)
        return r

    @steps.tracked("zpp", "Zero Product Property")
    def zpp(self):
        return System(Comparison(lhs, self.right) for lhs in self.left)

    @steps.tracked("flip", "Flip")
    def reverse(self) -> Comparison:
        """Write the comparison in reverse"""
        return Comparison(self.right, self.left, self.rel.reverse())

    @steps.tracked("normalize", "Normalize")
    def normalize(self) -> Comparison:
        """Put all terms on the lhs"""
        value = self.left - self.right
        register(value)
        return Comparison(value, Const(), self.rel)

    def reverse_sign(self, value: Node) -> CompRel:
        # Can safely flip sign based on coefficient:
        # solving.core.solve() will gracefully handle any mishaps
        if self.rel in {CompRel.EQ, CompRel.NE}:
            return self.rel
        value = value.canonical()[0]
        if value < 0:
            return self.rel.reverse()
        return self.rel

    @steps.tracked()
    def subs(self, mapping: dict[Node]) -> Comparison:
        left, right = self.left.subs(mapping), self.right.subs(mapping)
        register(left)
        register(right)
        return Comparison(left, right, self.rel)

    # @subs.check_changed

    @steps.tracked()
    def factor(self, left_only=False):
        left, right = self.left.factor(), self.right
        register(left, reason="Factor lhs")
        if not left_only:
            right = right.factor()
            register(right, reason="Factor rhs")
        return Comparison(left, right, self.rel)

    @steps.tracked()
    def expand(self):
        left, right = self.left.expand(), self.right.expand()
        register(left)
        register(right)
        return Comparison(left, right, self.rel)

    def totex(self, align: bool = False) -> str:
        left, rel, right = self.left, self.rel, self.right
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
