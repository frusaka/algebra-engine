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
from .utils import quadratic


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

    def approx(self, threshold: float = 1e-10):
        v = self.left.approx() - self.right.approx()
        if self.rel is not CompRel.EQ:
            return bool(Comparison(v, 0, self.rel))
        return abs(v) < threshold

    def __getitem__(self, value: Var) -> Comparison:
        """
        This method will be called when solving for a variable
        """
        # NOTE: if val>0:... checks are not necessary, they just make the solving process look natural
        ETSteps.register(ETNode(self))
        if value not in self:
            return self
        # Rewrite the comparison to put the target variable on the left
        if value in self.right and not value in self.left:
            self = self.reverse()
            ETSteps.register(ETNode(self))
        remove = []
        # Solving using the quadratic formula
        if res := quadratic(self, value):
            if len(res) == 1:
                res = Comparison(value, res.pop())
                ETSteps.register(ETNode(res))
            else:
                res = System(Comparison(value, root) for root in res)
                ETSteps.register(ETBranchNode(res))
            return res
        # Moving target terms to the left
        if self.right.__class__ is Add:
            for t in self.right:
                if value in t:
                    remove.append(t)
            if remove:
                return (self - Add.from_terms(remove, 0))[value]
        if value in self.right:
            return (self - self.right)[value]

        if self.left.__class__ is Add:
            if (
                utils.is_polynomial(self.left - self.right)
                and utils.degree(self.left) != 2
                and (f := (self.left - self.right).simplify()).__class__ is not Add
            ):
                if self.right:
                    self -= self.right
                    ETSteps.register(ETNode(self))
                ETSteps.register(ETTextNode("Factored Expression"))
                return Comparison(f, Const(0), self.rel)[value]
            for i in self.left:
                if not value in i:
                    remove.append(i)  # Not moving it yet, need to check for quadratics
                    continue
                # Node is in radical form
                if (
                    exp := math.lcm(
                        *(i[1].denominator for i in utils.flatten_factors(i))
                    )
                ) != 1:
                    self -= self.left - i
                    ETSteps.register(ETNode(self))
                    return (self**exp)[value]
            if remove:
                return (self - Add.from_terms(remove))[value]
            # Brute-force factorization
            gcd, v = self.left.cancel_gcd()
            # # Try remove unwanted terms
            unwanted = Mul.from_terms(
                i for i in (*Mul.flatten(gcd), v) if value not in i
            )
            if unwanted.__class__ is not Const:
                return (self / unwanted)[value]
            if gcd != 1 and not self.right:
                return Comparison(Mul(gcd, v), self.right, self.rel)[value]

        # Isolation by division
        if self.left.__class__ is Mul:
            for t in self.left:
                if not value in t or utils.hasremainder(t):
                    remove.append(t)
            if remove:
                return (self / Mul(*remove))[value]
            # Zero Product Property
            if self.right == 0:
                return System(Comparison(lhs, self.right) for lhs in self.left)[value]
        # Power lhs if it is a radical
        if (
            exp := max(i[1].denominator for i in utils.flatten_factors(self.left))
        ) != 1:
            return (self**exp)[value]
        # Power lhs if it is a radical
        if (exp := min(i[1].numerator for i in utils.flatten_factors(self.left))) != 1:
            if exp.__class__ is not int:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self ** Const(1, exp))[value]

        if self.left == value:
            return self

        if not utils.is_polynomial(self.left):
            raise ArithmeticError(f"Could not solve for {value}")
        # Purposefully expand lhs
        if utils.degree(self.left) == 2:
            ETSteps.register(ETTextNode("Expanded"))
            return Comparison(self.left.expand(), self.right, self.rel)[value]

        if not self.left.__class__ is Add or len(self.left.args) != 2:
            raise ArithmeticError(f"Could not solve for {value}")

        # Detect disguised quadratics
        a, b = sorted(self.left, key=utils.degree)
        p = utils.degree(a)
        if p * 2 != utils.degree(b):
            raise ArithmeticError(f"Could not solve for {value}")

        u = Var("u")
        a = a.canonical()[1]
        lhs = self.left.ast_subs({a: u})
        if utils.degree(lhs) != 2 or value in lhs:
            return self
        p = a.exp.numerator
        with ETSteps.branching(1) as br:
            for _ in br:
                ETSteps.register(ETTextNode(f"Disguised quadratic: u={a}"))
                res = Comparison(lhs, self.right, self.rel)[u]
                r = Const(1, p)
                a **= r
                roots = [Comparison(a, i.right**r) for i in res]
                if not p % 2:
                    roots.extend(Comparison(a, -i.right) for i in tuple(roots))
                ETSteps.register(ETOperatorNode(ETOperatorType.SQRT, p, 2))
        roots = System(roots)
        return System(roots)[value]

    def __contains__(self, value: Var) -> bool:
        return value in self.left or value in self.right

    def __sub__(self, value: Node) -> Comparison:
        if value.canonical()[0] > 0:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.SUB, value, len(str(self.left)) + 1)
            )
        else:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.ADD, -value, len(str(self.left)) + 1)
            )
        return Comparison(self.left - value, self.right - value, self.rel)

    def __truediv__(self, value: Node) -> Comparison:
        if value.as_numer_denom()[1] == 1:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.DIV, value, len(str(self.left)) + 1)
            )
        else:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.TIMES, value**-1, len(str(self.left)) + 1)
            )
        # Make sure to use long-division when applicable
        return Comparison(
            self.left / value, self.right / value, self.reverse_sign(value)
        )

    def __pow__(self, value: Const) -> Comparison:
        if value.denominator != 1 and value.numerator == 1:
            ETSteps.register(
                ETOperatorNode(
                    ETOperatorType.SQRT,
                    value.denominator,
                    len(str(self.left)) + 1,
                )
            )
        else:
            ETSteps.register(
                ETOperatorNode(ETOperatorType.POW, value, len(str(self.left)) + 1)
            )
        # Make sure to expand
        lhs = self.left**value
        rhs = (self.right**value).expand()
        # plus/minus trick for even roots
        if (
            (rhs != 0 or self.rel is not CompRel.EQ)
            and value.__class__ is Const
            and not value.denominator % 2
        ):
            return System({Comparison(lhs, rhs), Comparison(lhs, -rhs)})
        return Comparison(lhs, rhs, self.rel)

    def __bool__(self) -> bool:
        return getattr(operator, self.rel.name.lower())(self.left, self.right)

    def reverse(self) -> Comparison:
        """Write the comparison in reverse"""
        return Comparison(self.right, self.left, self.rel.reverse())

    def normalize(self) -> Comparison:
        """Put all terms on the lhs"""
        return Comparison(self.left - self.right, Const(), self.rel)

    def reverse_sign(self, value: Node) -> CompRel:
        # Can safely skip flipping sign:
        # operators.solve() will gracefully handle any mishaps
        if self.rel in {CompRel.EQ, CompRel.NE}:
            return self.rel
        if value.__class__ is not Const:
            try:
                value = value.approx()
            except:
                ETSteps.register(
                    ETTextNode(
                        f"Unknown sign of '{value}': resolving to finding roots",
                        "#ffc02b",
                    )
                )
                return CompRel.EQ
        if value < 0:
            return self.rel.reverse()
        return self.rel

    def ast_subs(self, mapping: dict) -> Comparison:
        return Comparison(
            self.left.ast_subs(mapping), self.right.ast_subs(mapping), self.rel
        )

    def simplify(self):
        return self

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
