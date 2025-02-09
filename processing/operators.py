from dataclasses import dataclass
from operator import *
from data_types import *
from typing import Any
from utils.constants import SYMBOLS


@dataclass
class Unary:
    """Unary operator: -n, +n, or maybe in the future, n!"""

    oper: Any
    value: Any

    def __repr__(self) -> str:
        return f"{SYMBOLS.get(self.oper.type.name)}{self.value}"


@dataclass
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
    var = var.value
    res = comp[var]
    if var in res and not isinstance(res.left.value, Variable):
        raise ArithmeticError(f"Could not solve for '{var}'")
    rhs = set(res.right) if isinstance(res.right, Solutions) else [res.right]

    # Check for extraneous solutions
    for i in tuple(rhs):
        try:
            if not Comparison(
                subs(comp.left, var, i), subs(comp.right, var, i), comp.rel
            ):
                if var in res and comp.rel is not CompRel.EQ:
                    print("WARNING: Test Solutions".join(("\033[33m", "\033[0m")))
                    break
                rhs.remove(i)
        except ZeroDivisionError:
            rhs.remove(i)
    if len(rhs) == 1:
        rhs = rhs.pop()
        # Infinite solutions
        if Comparison(res.left, rhs, comp.rel):
            rhs = Any
    # No solutions
    elif not rhs:
        rhs = None
    # Multiple solutions
    else:
        rhs = Solutions(rhs)
    rel = res.rel
    if rhs in (None, Any):
        rel = CompRel.EQ
    return Comparison(Term(value=var), rhs, rel)


def root(a: Term, b: Term) -> Term:
    return b**a.inv


def bool(a: Term | Comparison) -> bool:
    return getattr(a, "__bool__", lambda: a.value != 0)()


def ratio(a: Term, b: Term) -> Term:
    a, b = Term.rationalize(a / b, Term())
    if not isinstance(b.value, Number) or b.exp != 1:
        return Product.resolve(a, b.inv)
    return a.scale(b.inv.value)
