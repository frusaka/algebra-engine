from dataclasses import dataclass
from functools import lru_cache
from operator import *
from data_types import *
from typing import Any
from .tokens import Token
from utils.constants import SYMBOLS


@dataclass(frozen=True)
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Token
    value: Any

    def __repr__(self) -> str:
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass(frozen=True)
class Binary:
    """Unary operator: arithmetic (+-*/) or exponetiation"""

    oper: Token
    left: Any
    right: Any

    def __repr__(self) -> str:
        return f"({self.left} {SYMBOLS.get(self.oper.type.name)} {self.right})"


def eq(a: Any, b: Any) -> Comparison:
    return Comparison(a, b)


def gt(a: Any, b: Any) -> Comparison:
    return Comparison(a, b, CompRel.GT)


def lt(a: Any, b: Any) -> Comparison:
    return Comparison(a, b, CompRel.LT)


def le(a: Any, b: Any) -> Comparison:
    return Comparison(a, b, CompRel.LE)


def ge(a: Any, b: Any) -> Comparison:
    return Comparison(a, b, CompRel.GE)


def subs(a: Term | Comparison, mapping: dict[Variable, Term]) -> Term | Comparison:
    """Substitute all occurances of `var` with the provided value"""
    from processing import Interpreter, AST

    val = str(a)
    for i in mapping:
        val = val.replace(i, i.join(("({", "})")))
    return Interpreter().eval(AST(val.format_map(mapping)))


@lru_cache
def solve(
    var: Variable | tuple[Variable], comp: Comparison | System, reject=True
) -> Comparison | System:
    res = comp[var]
    if reject:
        print("Verifying solutions...".join(("\033[34m", "\033[0m")))
    if var in res and not isinstance(res.left.value, Variable):
        raise ArithmeticError(f"Could not solve for '{var}'")
    # Nested System: multple solution
    if isinstance(comp, System):
        if any(isinstance(i, System) for i in res):
            res = set(res)
            for i in tuple(res):
                if not subs(comp, dict((j.left.value, j.right) for j in i)):
                    print(f"Extraneous: {i}".join(("\033[31m", "\033[0m")))
                    res.remove(i)
            if len(res) == 1:
                return res.pop()
            if not res:
                return System(Comparison(Term(value=Variable(i)), None) for i in var)
            return System(res)
        res_2 = subs(comp, dict((i.left.value, i.right) for i in res))
        for i in res_2:
            if not i:
                print(f"Extraneous: {i}".join(("\033[31m", "\033[0m")))
                return System(Comparison(Term(value=Variable(i)), None) for i in var)
        return res
    sol = set(res) if isinstance(res, System) else {res}
    # Verify Solutions
    for i in tuple(sol):
        try:
            if not subs(comp, {var: i.right}):
                # Atleast check for boundary values
                if (
                    var in i
                    and comp.rel is not CompRel.EQ
                    and subs(comp.left, {var: i.right})
                    == subs(comp.right, {var: i.right})
                ):
                    print(f"Boundary: {i}".join(("\033[33m", "\033[0m")))
                    continue
                if not reject:
                    continue
                print(f"Extraneous: {i}".join(("\033[31m", "\033[0m")))
                sol.remove(i)
        except ZeroDivisionError:
            print(f"Undefined: {i}".join(("\033[31m", "\033[0m")))
            sol.remove(i)
    if len(sol) == 1:
        sol = sol.pop()
        # Infinite solutions
        if isinstance(res, Comparison) and res:
            return Comparison(Term(value=var), Any)
        # One solution
        return sol
    # No solutions
    if not sol:
        return Comparison(Term(value=var), None)
    # Multiple solutions
    return System(sol)


def root(a: Term, b: Term) -> Term:
    return b**a.inv


def bool(a: Term | Comparison) -> bool:
    return getattr(a, "__bool__", lambda: a.value != 0)()


def ratio(a: Term, b: Term) -> Term:
    a, b = Term.rationalize(a / b, Term())
    if not isinstance(b.value, Number) and not isinstance(a.value, Number):
        return Product.resolve(a, b.inv)
    if isinstance(b.value, Number):
        return a.scale(b.inv.value)
    return a * b.inv
