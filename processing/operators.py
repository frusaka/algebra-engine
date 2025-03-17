from functools import lru_cache
from typing import Any, Sequence
from operator import *
from datatypes import *


def eq(a: Term, b: Term) -> Comparison:
    return Comparison(a, b)


def gt(a: Term, b: Term) -> Comparison:
    return Comparison(a, b, CompRel.GT)


def lt(a: Term, b: Term) -> Comparison:
    return Comparison(a, b, CompRel.LT)


def le(a: Term, b: Term) -> Comparison:
    return Comparison(a, b, CompRel.LE)


def ge(a: Term, b: Term) -> Comparison:
    return Comparison(a, b, CompRel.GE)


def subs(a: Term | Comparison, mapping: dict[Variable, Term]) -> Term | Comparison:
    """Substitute all occurances of `var` with the provided value"""
    from processing import Interpreter, AST

    val = str(a)
    for i in mapping:
        val = val.replace(i, i.join(("({", "})")))
    return Interpreter().eval(AST(val.format_map(mapping)))


def validate_solution(
    org: System | Comparison, sol: System | Comparison, mapping: dict
) -> bool:
    try:
        if not (subs(org.normalize(), mapping) if mapping else sol.normalize(False)):
            title = "Extraneous" if mapping else "Contradiction"
            print(f"{title}: {sol}".join(("\033[31m", "\033[0m")))
            return False
        return True
    except ZeroDivisionError:  # Higly unlikely
        print(f"Zero division: {sol}".join(("\033[31m", "\033[0m")))
    except AttributeError:
        print(f"Malformed: {sol}".join(("\033[31m", "\033[0m")))
    return False


@lru_cache(maxsize=20)
def solve(
    var: Variable | Sequence[Variable], comp: Comparison | System
) -> Comparison | System:
    res = comp[var]
    s = "s" * isinstance(res, System)
    print(f"Verifying solution{s}".join(("\033[34m", "\033[0m")))
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
                            j.right
                            for j in sorted(i, key=lambda k: var.index(k.left.value))
                        )
                    )
            if len(res) == 1:
                return Comparison(var, res.pop())
            if not res:
                return Comparison(var, Collection())
            return Comparison(var, Collection(res))
        if not validate_solution(comp, res, dict((j.left.value, j.right) for j in res)):
            return Comparison(var, Collection())
        return Comparison(
            var,
            tuple(j.right for j in sorted(res, key=lambda k: var.index(k.left.value))),
        )
    sol = set(res) if isinstance(res, System) else {res}
    # Verify Solutions
    for i in tuple(sol):
        if not validate_solution(
            comp, i, {var: i.right} if i.left.value == var else {}
        ):
            sol.remove(i)
    if len(sol) == 1:
        sol = sol.pop()
        # One solution
        if var in sol:
            return Comparison(var, sol.right, sol.rel)
        # Infinite solutions
        if sol.normalize(0):
            if sol.rel is CompRel.EQ or var not in comp:
                return Comparison(var, Collection("ℂ"))
            return Comparison(var, Collection("ℝ"))
        sol = None
    # Making sense of perfect radical solutions
    elif len({i.right for i in sol}) == 1:
        if comp.rel is CompRel.LE:
            return Comparison(var, sol.pop().right)
        if comp.rel is CompRel.GT:
            return Comparison(var, sol.pop().right, CompRel.NE)
        if comp.rel is CompRel.GE:
            return Comparison(var, Collection("ℝ"))
        sol = None

    # No solutions
    if not sol:
        return Comparison(var, Collection())
    # Multiple solutions
    if comp.rel is CompRel.EQ:
        return Comparison(var, Collection(i.right for i in sol))
    return Comparison(var, Range(sol, comp.rel.name.startswith("L")))


def root(a: Term, b: Term) -> Term:
    return b**a.inv
