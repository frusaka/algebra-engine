from typing import Iterable

import math
from itertools import product
from functools import reduce

from datatypes.base import Node
from solving.utils import domain_restriction

from .interval import Interval, INF
from .solutions import IntervalUnion, SolutionSet
from .system import System
from .comparison import Comparison, CompRel
from .eval_trace import *

from datatypes.nodes import Pow, Var, Float


def to_float(val: Node | None, scale: int = -1) -> float:
    if val is None:
        return float("inf") * scale
    return val.approx()


def merge_intervals(intervals: list[Interval]) -> list[Interval]:
    if len(intervals) <= 1:
        return intervals

    # Sort by start, and treat closed starts as earlier than open ones when equal
    intervals.sort(key=lambda i: (to_float(i.start), i.open[0]))

    merged = []
    c = intervals[0]
    for n in intervals[1:]:
        c_end = to_float(c.end, 1)
        c_open_left, c_open_right = c.open
        n_start, n_end = to_float(n.start), to_float(n.end, 1)
        n_open_right = n.open[1]

        if not (
            n_start < c_end
            or (math.isclose(n_start, c_end) and not (n.open[0] or c.open[1]))
        ):
            if c.start == c.end:
                merged.append(SolutionSet([c.start]))
            else:
                merged.append(c)
            c = n
            continue

        # Compute merged start
        new_start = c.start
        new_open_left = c_open_left

        # Compute merged end
        if n_end > c_end:
            new_end = n.end
            new_open_right = n_open_right
        elif n_end == c_end:
            new_end = c.end
            new_open_right = c_open_right and n_open_right
        else:
            new_end = c.end
            new_open_right = c_open_right and n_open_right

        c = Interval(new_start, new_end, open=(new_open_left, new_open_right))
    merged.append(c)
    return merged


def split_domain_by_roots(
    domain: Interval, roots: list[Node], open: bool
) -> list[Interval]:

    roots = [i for i in roots if i * 0.999 in domain]
    if not roots:
        return [domain]
    res = []
    roots = [domain.start, *roots, domain.end]
    for i in range(len(roots) - 1):
        left_open = domain.open[0] if i == 0 else open
        right_open = domain.open[1] if i + 2 == len(roots) else open
        res.append(Interval(roots[i], roots[i + 1], (left_open, right_open)))
    return res


def test_intervals(
    intervals: list[Interval],
    org: Comparison,
    var: Var,
    verbose: bool = True,
):
    if verbose:
        s = "s" * (bool(len(intervals) - 1))
        ETSteps.register(ETTextNode(f"Testing interval{s}", "#0d80f2"))

    valid = []
    for interval in intervals:
        a, b = interval.start, interval.end
        if a is b is None:
            a = -10000
            b = 5
        if a is None:
            a = b - 100
        if b is None:
            b = a + 100
        if try_subs_interval(org, interval, {var: Float((a + b) / 2)}, verbose):
            valid.append(interval)
    valid = merge_intervals(valid)
    if not valid:
        return SolutionSet()
    if len(valid) == 1:
        return valid.pop()
    return IntervalUnion(valid)


def interpolate_roots(
    var: Var,
    org: Comparison,
    roots: Iterable[Node],
    domain: Interval | IntervalUnion,
    verbose=True,
):

    open = org.rel.name == "NE" or not org.rel.name.endswith("E")
    try:
        roots = sorted(
            (t for t in roots if not t.approx().imag), key=lambda t: t.approx()
        )
    except AttributeError:
        raise ValueError("Multivariate inequality")
    if isinstance(domain, IntervalUnion):
        intervals = [i for j in domain for i in split_domain_by_roots(j, roots, open)]
    else:
        intervals = split_domain_by_roots(domain, roots, open)
    # Try testing points
    return test_intervals(intervals, org, var, verbose)


def try_subs_interval(
    org: Comparison, interval, mapping: dict[Var, Node], verbose: bool = True
) -> bool:
    try:
        res = org.subs(mapping).is_close()
    except:
        res = False
    if verbose:
        ETSteps.register(ETVerifyNode(interval, res))
    return res


def intersect_domains(domains: Iterable[Iterable[Interval]]) -> list[Interval]:
    res = []
    for vals in product(*domains):
        i = vals[0]
        for j in vals[1:]:
            i = i.intersect(j)
            if not i:
                break
        if i:
            res.append(i)
    res.sort(key=lambda i: to_float(i.start))
    return res


def evaluate_domain(var: Var, org: Comparison) -> Interval | IntervalUnion:
    restr = domain_restriction(org.left, var) + domain_restriction(org.right, var)
    with ETSteps.branching(1) as br:
        next(br)
        ETSteps.register(ETTextNode("Evaluating domain"))
        if not restr:
            ETSteps.register(ETNode(Comparison(var, INF, CompRel.IN)))
            return INF
        res = []
        with ETSteps.branching(len(restr)) as br:
            for idx, eqn in zip(br, restr):
                ETSteps.register(ETTextNode(f"Branch {idx+1}"))
                ans = eqn.solve_for(var)
                if ans.__class__ is not System:
                    ans = [ans]
                res.append((eqn, ans))
        # Unnesting single domain restriction
        if len(restr) == 1:
            ETSteps.data[-1][1:] = ETSteps.data[-1][1][1:]
        intervals = []
        for org, ans in res:
            res = interpolate_roots(var, org, {i.right for i in ans}, INF, False)
            if not isinstance(res, IntervalUnion):
                res = (res,)
            intervals.append(res)
        res = intersect_domains(intervals)
        if len(res) == 1:
            res = res.pop()
        else:
            res = IntervalUnion(res)
        ETSteps.register(ETNode(Comparison(var, res, CompRel.IN)))
    return res


def validate_roots(roots: Iterable[Node]) -> set[Node]:
    try:
        return set(i for i in roots if not i.approx().imag)
    except AttributeError:
        raise ValueError("roots contain variables")


def validate_solution(
    org: System | Comparison, sol: System | Comparison, mapping: dict, verbose=True
) -> bool:
    res = 1
    try:
        if not (
            v := (
                org.normalize().subs(mapping).expand() if mapping else sol.normalize()
            )
        ):
            if v.is_close():
                res = 2
            else:
                res = 0
    except:
        res = 0
    if verbose:
        ETSteps.register(
            ETVerifyNode(sol if sol.__class__ is Comparison else ETBranchNode(sol), res)
        )
    return res


def verify_systems(
    vars: tuple[Var], org: System | System, solutions: Iterable[System]
) -> set[Comparison]:
    res = set()
    for i in solutions:
        d = {j.left: j.right for j in i if j.left in vars}
        if validate_solution(org, i, d):
            res.add(tuple(map(d.get, vars)))
    return res


def solve_ineq(var, ineq: Comparison):
    # First evaluate Domain
    domain = evaluate_domain(var, ineq)

    # Second find roots
    with ETSteps.branching(1) as br:
        next(br)
        ETSteps.register(ETTextNode("Finding Roots"))
        res = Comparison(ineq.left, ineq.right).solve_for(var)

    if isinstance(res, Comparison):
        if res.left != var:
            roots = []
        else:
            roots = [res.right]
    else:
        roots = [i.right for i in res]

    # Third split domain by roots
    return Comparison(var, interpolate_roots(var, ineq, roots, domain), CompRel.IN)


def get_vars(expr):
    if expr.__class__ is Var:
        return {expr}
    if expr.__class__ is Pow:
        return get_vars(expr.base).union(get_vars(expr.exp))
    if expr.__class__ is Comparison:
        return get_vars(expr.left).union(get_vars(expr.right))
    if hasattr(expr, "__iter__"):
        return reduce(lambda a, b: a.union(b), map(get_vars, expr))
    return set()


def solve(src: Comparison | System, *var: Var) -> Comparison | System:
    if not var:
        var = tuple(sorted(get_vars(src)))
    if not var:
        return bool(src)
    var = tuple(Var(i) if not isinstance(i, Var) else i for i in var)
    if src.__class__ is Comparison:
        if len(var) > 1:
            ETSteps.register(ETTextNode(f"Solving for {var}"))
            res = []
            with ETSteps.branching(len(var)) as br:
                for _, v in zip(br, var):
                    sol = solve(src, v)
                    ETSteps.register(ETNode(sol))
                    res.append(sol)
            return System(res)
        var = var[0]
        ETSteps.register(ETTextNode(f"Solving for {var}"))
        if src.rel is not CompRel.EQ:
            return solve_ineq(var, src)
    elif len(var) != len(v2 := get_vars(src)):
        raise TypeError(f"solve() expected {v2}, got {var} instead")
    res = src.solve_for(var)
    s = "s" * isinstance(res, System)
    ETSteps.register(ETTextNode(f"Verifying solution{s}", "#0d80f2"))

    if isinstance(src, System):
        if len(res) == 0:
            # print()
            sol = res
        else:
            if not next(iter(res)).__class__ is System:
                res = [res]
            sol = verify_systems(var, src, res)
    else:
        if isinstance(res, Comparison) and res.left != var:
            if validate_solution(src, res, {}):
                return Comparison(var, INF, CompRel.IN)
            return Comparison(var, SolutionSet(), CompRel.IN)
        if not isinstance(res, System):
            res = [res]
        sol = {i.right for i in res if validate_solution(src, i, {var: i.right})}
    # One solution
    if len(sol) == 1:
        return Comparison(var, sol.pop())
    # Multiple or No solution
    return Comparison(var, SolutionSet(sol), CompRel.IN)
