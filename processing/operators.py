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
            if sol.rel in {CompRel.LT, CompRel.GT}:
                print(f"Boundary: {sol}".join(("\033[33m", "\033[0m")))
        return True
    except ZeroDivisionError:
        print(f"Zero division: {sol}".join(("\033[31m", "\033[0m")))
    return False


@lru_cache
def solve(
    var: Variable | tuple[Variable], comp: Comparison | System, finalize=True
) -> Comparison | System:
    res = comp[var]
    if res is None:
        return Comparison(var, None)
    if finalize:
        print(
            f"Verifying solution{"s"*(isinstance(res, System))}...".join(
                ("\033[34m", "\033[0m")
            )
        )
    if var in res and not isinstance(res.left.value, Variable):
        raise ArithmeticError(f"Could not solve for '{var}'")
    # Nested System: multple solution
    if isinstance(comp, System):
        if any(isinstance(i, System) for i in res):
            res = set(res)
            for i in tuple(res):
                res.remove(i)
                if validate_solution(comp, i, dict((j.left.value, j.right) for j in i)):
                    res.add(
                        tuple(
                            next(j.right for j in i if j.left.value == k) for k in var
                        )
                    )
            if len(res) == 1:
                return Comparison(var, res.pop())
            if not res:
                return Comparison(var, None)
            return Comparison(var, Collection(res))
        if not validate_solution(comp, res, dict((j.left.value, j.right) for j in res)):
            return Comparison(var, None)
        return Comparison(
            var, tuple(next(j.right for j in res if j.left.value == k) for k in var)
        )
    sol = set(res) if isinstance(res, System) else {res}
    # Verify Solutions
    for i in tuple(sol):
        if not validate_solution(comp, i, {var: i.right}):
            sol.remove(i)
    if len(sol) == 1:
        sol = sol.pop()
        # Infinite solutions
        if sol:
            return Comparison(var, "Any")
        # One solution
        elif var in sol:
            if finalize:
                return Comparison(var, sol.right, sol.rel)
            return sol
        sol = None
    # No solutions
    if not sol:
        return Comparison(var, None)
    # Multiple solutions
    if comp.rel is CompRel.EQ:
        return Comparison(var, Collection(i.right for i in sol))
    return Comparison(var, Range(sol, comp.rel.name.startswith("L")))


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
