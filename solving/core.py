import math
from typing import Iterable

from datatypes.base import Node

from .interval import Interval
from .solutions import IntervalUnion, SolutionSet
from .system import System
from .comparison import Comparison, CompRel
from .eval_trace import *

from datatypes.nodes import Const, Var


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

    roots = [i for i in roots if i * Const(9999, 10000) in domain]
    if not roots:
        return roots
    res = []
    roots = [domain.start, *roots, domain.end]
    for i in range(len(roots) - 1):
        left_open = domain.open[0] if i == 0 else open
        right_open = domain.open[1] if i + 1 == len(roots) else open
        res.append(Interval(roots[i], roots[i + 1], (left_open, right_open)))
    return res


def test_intervals(
    intervals: list[Interval], org: Comparison, var: Var, verbose: bool = True
):

    valid = []
    for interval in intervals:
        a, b = interval.start, interval.end
        if a is b is None:
            a = -10000
            b = Const(5)
        if a is None:
            a = b - 100
        if b is None:
            b = a + 100
        if try_subs_interval(org, interval, {var: (a + b) / 2}, verbose):
            valid.append(interval)
    valid = merge_intervals(valid)
    if not valid:
        return SolutionSet()
    if len(valid) == 1:
        return valid.pop()
    return IntervalUnion(valid)


def interpolate_roots(
    var: Var, org: Comparison, roots: Iterable[Node], check_domain=True, verbose=True
):

    open = org.rel.name == "NE" or not org.rel.name.endswith("E")
    roots = sorted(roots, key=lambda t: t.approx())
    if check_domain:
        domain = evaluate_domain(var, org)
    else:
        domain = Interval(None, None, (True, True))
    if isinstance(domain, IntervalUnion):
        intervals = [
            i for j in domain for i in split_domain_by_roots(j, roots, open)
        ] or domain
    else:
        intervals = split_domain_by_roots(domain, roots, open) or [domain]
    # Try testing points
    return test_intervals(intervals, org, var, verbose)


def try_subs_interval(
    org: Comparison, interval, mapping: dict[Var, Node], verbose: bool = True
) -> bool:
    try:
        res = org.ast_subs(mapping).approx()
    except:
        res = False
    if verbose:
        ETSteps.register(ETVerifyNode(interval, res))
    return res


def resolve_domains(domains: list[Interval]) -> list[Interval]:
    if len(domains) <= 1:
        return domains

    res = [domains[0]]
    for i in domains[1:]:
        found = 0
        for idx, j in enumerate(res):
            if inter := i.intersect(j):
                res[idx] = inter
                found = 1
        if not found:
            res.append(i)
    return res


def evaluate_domain(var: Var, org: Comparison):
    restr = org.left.domain_restriction(var) + org.right.domain_restriction(var)
    if not restr:
        return Interval(None, None, (True, True))
    prev = ETSteps.history[-1].pop()
    with ETSteps.branching(1) as br:
        for _ in br:
            ETSteps.register(ETTextNode("Evaluating domain", "#0d80f2"))
            if len(restr) == 1:
                lhs, rel = restr[0]
                res = Comparison(lhs, Const(0), getattr(CompRel, rel))[var]
            else:

                res = System(
                    Comparison(lhs, Const(0), getattr(CompRel, rel))
                    for lhs, rel in restr
                )[var]
        if res.__class__ is not System:
            res = [res]
        intervals = []
        for i in res:
            res = interpolate_roots(var, i, {i.right}, False, False)
            if isinstance(res, IntervalUnion):
                intervals.extend(res)
            else:
                intervals.append(res)
        res = resolve_domains(intervals)
        if len(res) == 1:
            res = res.pop()
        else:
            res = IntervalUnion(res)
        ETSteps.register(ETNode(Comparison(var, res, CompRel.IN)))
    ETSteps.register(prev)
    return res


def validate_roots(roots: Iterable[Node]) -> set[Node]:
    try:
        return set(i for i in roots if not i.approx().imag)
    except AttributeError:
        raise ValueError("roots contain variables")


def validate_solution(
    org: System | Comparison, sol: System | Comparison, mapping: dict
) -> bool:
    res = 1
    try:
        if not (
            v := (
                org.normalize().ast_subs(mapping).expand()
                if mapping
                else sol.normalize()
            )
        ):
            if v.approx():
                res = 2
            else:
                res = 0
    except:
        res = 0
    ETSteps.register(
        ETVerifyNode(sol if sol.__class__ is Comparison else ETBranchNode(sol), res)
    )
    return res


def verify_systems(
    vars: Var, org: System | System, solutions: Iterable[System]
) -> set[Comparison]:
    res = set()
    for i in solutions:
        if validate_solution(org, i, {j.left: j.right for j in i}):
            res.add(tuple(j.right for j in sorted(i, key=lambda k: vars.index(k.left))))
    return res


def solve(var: Var | tuple[Var], comp: Comparison | System) -> Comparison | System:
    ETSteps.clear()
    if comp.__class__ is Comparison:
        ETSteps.register(ETTextNode(f"Solving for {var}"))

    res = comp[var]
    s = "s" * isinstance(res, System)
    ETSteps.register(ETTextNode(f"Verifying solution{s}", "#0d80f2"))

    if isinstance(comp, System):
        if not next(iter(res)).__class__ is System:
            res = [res]
        sol = verify_systems(var, comp, res)
    else:
        if isinstance(res, Comparison) and res.left != var:
            if validate_solution(comp, res, {}):
                # lhs==rhs : only domain restriction matters
                return Comparison(var, evaluate_domain(var, comp), CompRel.IN)
            return Comparison(var, SolutionSet(), CompRel.IN)
        if not isinstance(res, System):
            res = [res]
        if comp.rel is not CompRel.EQ:
            return Comparison(
                var, interpolate_roots(var, comp, [i.right for i in res]), CompRel.IN
            )

        sol = {i.right for i in res if validate_solution(comp, i, {var: i.right})}
    # One solution
    if len(sol) == 1:
        return Comparison(var, sol.pop())
    # Multiple or No solution
    return Comparison(var, SolutionSet(sol), CompRel.IN)
