from typing import Iterable

import math
from itertools import product

from datatypes.base import Node
from utils import steps
from utils.steps import *
from .utils import domain_restriction, get_vars

from .interval import Interval, INF
from .solutions import IntervalUnion, SolutionSet
from .system import System
from .comparison import Comparison, CompRel

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
    valid = []
    with steps.scoped(inner := []):
        for interval in intervals:
            a, b = interval.start, interval.end
            if a is b is None:
                a = -10000
                b = 5
            if a is None:
                a = b - 100
            if b is None:
                b = a + 100
            if res := try_subs_interval(org, interval, {var: Float((a + b) / 2)}):
                valid.append(interval)
            if verbose:
                register(res)
    valid = merge_intervals(valid)
    if not valid:
        res = SolutionSet()
    elif len(valid) == 1:
        res = valid.pop()
    else:
        res = IntervalUnion(valid)
    if verbose:
        s = "s" * (bool(len(intervals) - 1))
        steps.register(Step(f"Testing interval{s}", ETNode(res), inner))
    return res


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


@steps.tracked("VERIFY")
def try_subs_interval(org: Comparison, interval, mapping: dict[Var, Node]) -> bool:
    try:
        v = org.subs(mapping)
        register(v)
        return v.is_close()
    except:
        return False


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


@steps.tracked("domain", "Evaluate domain")
def evaluate_domain(var: Var, org: Comparison) -> Interval | IntervalUnion:
    restr = domain_restriction(org.left, var) + domain_restriction(org.right, var)
    if not restr:
        return INF

    res = []

    for idx, eqn in enumerate(restr, 1):
        with scoped(inner := []):
            ans = eqn.solve_for(var)
        if steps.verbose():
            if len(restr) > 1:
                steps.register(Step(f"Branch {idx}", ETNode(ans), inner))
            else:
                [register(i) for i in inner]
        if ans.__class__ is not System:
            ans = [ans]
        res.append((eqn, ans))

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
    inner = []
    try:
        with steps.scoped(inner):
            v = org.subs(mapping).expand() if mapping else sol
            register(v)
            if not (v):
                if v := v.is_close():
                    res = 2
                else:
                    res = 0
                register(v)
    except:
        res = 0
    if verbose:
        register(
            Step(
                "Verify",
                ETOperator(
                    "VERIFY",
                    (sol,) if sol.__class__ is Comparison else (ETBranch(sol),),
                    res,
                ),
                inner,
            )
        )
    return res


def verify_systems(
    vars: tuple[Var], org: System, solutions: Iterable[System]
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
    register(domain)

    # Second find roots
    with steps.scoped(inner := []):
        res = Comparison(ineq.left, ineq.right).solve_for(var)
    register(Step("Finding Roots", ETNode(res), inner))
    if isinstance(res, Comparison):
        if res.left != var:
            roots = []
        else:
            roots = [res.right]
    else:
        roots = [i.right for i in res]

    # Third split domain by roots
    return Comparison(var, interpolate_roots(var, ineq, roots, domain), CompRel.IN)


@steps.tracked("solve")
def solve(src: Comparison | System, *var: Var) -> Comparison | System:
    if not var:
        var = tuple(sorted(get_vars(src)))
    if not var:
        return bool(src)

    def fin(var, res):
        if isinstance(src, System) or len(var) > 1:
            if len(res) == 0:
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

    var = tuple(Var(i) if not isinstance(i, Var) else i for i in var)
    if src.__class__ is Comparison:
        if len(var) > 1:
            res = []
            for v in var:
                with steps.scoped(inner := []):
                    res.append((v, src.solve_for(v)))
                steps.register(Step(f"Solve for {v}", ETNode(res[-1][-1]), inner))
            # [register(i[1]) for i in res]
            out = []
            with steps.scoped(inner := []):
                for k, v in res:
                    out.append(fin(k, v))
            register(Step(f"Verifying solutions", ETNode(""), inner))
            return System(out)
        else:
            var = var[0]
            if src.rel is not CompRel.EQ:
                return solve_ineq(var, src)
            res = src.solve_for(var)
    elif set(var) != (v2 := get_vars(src)) or len(var) > len(v2):
        raise TypeError(f"solve() expected {v2}, got {var} instead")
    else:
        res = src.solve_for(var)
    s = "s" * isinstance(res, System)

    with steps.scoped(inner := []):
        res = fin(var, res)
    register(Step(f"Verifying solution{s}", ETNode(res), inner))
    return res
