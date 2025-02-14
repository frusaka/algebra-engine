from dataclasses import dataclass
from operator import *
from data_types import *
from typing import Any
from utils.constants import SYMBOLS


@dataclass(frozen=True)
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Any
    value: Any

    def __repr__(self) -> str:
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass(frozen=True)
class Binary:
    """Unary operator: arithmetic (+-*/) or exponetiation"""

    oper: Any
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


def subs(a: Term | Comparison, var: Variable, value: Any) -> Term | Comparison:
    """Substitute all occurances of `var` with the provided value"""
    from processing import Interpreter, AST

    return Interpreter().eval(AST(str(a).replace(var, str(value).join("()"))))


def solve(var: Variable, comp: Comparison) -> Comparison:
    if isinstance(var, Term):
        var = var.value
    res = comp[var]
    if var in res and not isinstance(res.left.value, Variable):
        raise ArithmeticError(f"Could not solve for '{var}'")
    print("Verifying solutions...".join(("\033[34m", "\033[0m")))
    sol = set(res) if isinstance(res, System) else {res}

    # Check for extraneous solutions
    for i in tuple(sol):
        try:
            if not Comparison(
                subs(comp.left, var, i.right), subs(comp.right, var, i.right), comp.rel
            ):
                # Atleast check for boundary values
                if (
                    var in i
                    and comp.rel is not CompRel.EQ
                    and subs(comp.left, var, i.right) == subs(comp.right, var, i.right)
                ):
                    print(f"Boundary: {i}".join(("\033[33m", "\033[0m")))
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
