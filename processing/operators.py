from functools import lru_cache
from typing import Any
from operator import *
from datatypes import *


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


def log_extr(sol) -> bool:
    print(
        f"Extraneous: {sol}".join(("\033[31m", "\033[0m")),
        sep="\n",
    )
    return False


def validate_solution(
    org: System | Comparison, sol: System | Comparison, mapping: dict
) -> bool:
    try:
        if not subs(org.normalize(), mapping):
            return log_extr(sol)
        if isinstance(sol, Comparison) and not sol:
            if not isinstance(sol.left.value, Variable):
                return log_extr(sol)
            if sol.rel is not CompRel.EQ:
                print(f"Boundary: {sol}".join(("\033[33m", "\033[0m")))
        return True
    except ZeroDivisionError:
        print(f"Zero division: {sol}".join(("\033[31m", "\033[0m")))
    return False


@lru_cache
def solve(
    var: Variable | tuple[Variable], comp: Comparison | System, verbose=True
) -> Comparison | System:
    res = comp[var]
    if verbose:
        print("Verifying solutions...".join(("\033[34m", "\033[0m")))
    if var in res and not isinstance(res.left.value, Variable):
        raise ArithmeticError(f"Could not solve for '{var}'")
    # Nested System: multple solution
    if isinstance(comp, System):
        if any(isinstance(i, System) for i in res):
            res = set(res)
            for i in tuple(res):
                if not validate_solution(
                    comp, i, dict((j.left.value, j.right) for j in i)
                ):
                    res.remove(i)
            if len(res) == 1:
                return res.pop()
            if not res:
                return System(Comparison(Term(value=Variable(i)), None) for i in var)
            return System(res)
        if not validate_solution(comp, res, dict((j.left.value, j.right) for j in res)):
            return System(Comparison(Term(value=Variable(i)), None) for i in var)
        return res
    sol = set(res) if isinstance(res, System) else {res}
    # Verify Solutions
    for i in tuple(sol):
        if not validate_solution(comp, i, {var: i.right}):
            sol.remove(i)
    if len(sol) == 1:
        sol = sol.pop()
        # Infinite solutions
        if sol:
            return Comparison(Term(value=var), "Any")
        # One solution
        elif var in sol:
            return sol
        sol = None
    # No solutions
    if not sol:
        return Comparison(Term(value=var), "None")
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
