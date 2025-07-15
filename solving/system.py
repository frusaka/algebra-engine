from __future__ import annotations
import itertools
import math
from typing import Iterable, Sequence, TYPE_CHECKING


from datatypes.base import Node


from .eval_trace import *

from datatypes import *
from .utils import arrange_eqns, next_eqn
from utils.print_ import print_system
import utils

if TYPE_CHECKING:
    from .comparison import Comparison


def leading(f: Add, vars):
    # leading term using lex order
    res = {}
    for i in Add.flatten(f):
        v = i.canonical()[1]
        if v is None:
            res[i] = (0,)
            continue
        k = dict(utils.mult_key(i, 1) for i in Mul.flatten(v, 0))
        res[i] = tuple(k.get(vars[i], 0) for i in range(len(vars)))
    return max(res, key=res.get)


def spolynomial(f: Add, g: Add, vars):
    lt_f = leading(f, vars)
    lt_g = leading(g, vars)
    lcm = utils.lcm(lt_f.canonical()[1] or 1, lt_g.canonical()[1] or 1)
    return g.multiply(lcm / lt_g) - f.multiply(lcm / lt_f)


def reduce(f, G, vars):
    def divide(a, b, vars):
        q = []
        leading_b = leading(b, vars)
        while a:
            if utils.hasremainder(fac := (leading(a, vars) / leading_b)):
                break
            a += b.multiply(-fac)
            q.append(fac)
        return nodes.Add(*q), a

    r = f
    while r:
        divided = False
        for g in G:
            # Try single division step
            q, rem = divide(r, g, vars)
            if q:
                r = rem
                divided = True
                break  # Restart with updated r
        if not divided:
            break
    return r


def buchberger(G: list[Add], vars: list[Var]) -> list[Add | Node]:
    G = G.copy()
    pairs = list(itertools.combinations(range(len(G)), 2))

    while pairs:
        i, j = pairs.pop(0)
        S = spolynomial(G[i], G[j], vars)
        R = reduce(S, G, vars)
        if R:
            # Inconsistent?
            if R.__class__ is Const:
                return []
            G.append(R)
            new_idx = len(G) - 1
            for k in range(new_idx):
                pairs.append((k, new_idx))

    reduced = []
    for i, f in enumerate(G):
        r = reduce(f, reduced, vars)
        if not r:
            continue
        if r.__class__ is Add:
            if (d := math.lcm(*(i.canonical()[0].denominator for i in r))) > 1:
                r = r.multiply(d)
            if (g := math.gcd(*(i.canonical()[0].numerator for i in r))) > 1:
                r = r.multiply(Const(1, g))
            reduced.append(r)
        else:
            reduced.append(r.as_ratio()[0])
    return reduced


def compute_grobner(eqns: Iterable[Comparison], vars: list[Var], sort_vars=True):
    from .comparison import Comparison

    if sort_vars:
        eqns = arrange_eqns(eqns, vars)
        eqns = sorted(eqns, key=eqns.get)
        vars.reverse()
    G = buchberger([eqn.normalize().left.as_ratio()[0].expand() for eqn in eqns], vars)
    return set(Comparison(t, Const(0)) for t in G)


def _solve(eqns: set, org, v, sols):
    eqn = org.solve_for(v)
    eqns.remove(org)
    if eqn.__class__ is System:
        ETSteps.register(ETSubNode(v, ETBranchNode(i.right for i in eqn)))
        new_eqns = []
        for i in eqn:
            if i.left != v:
                continue
            new_eqns.append(
                (
                    System([j.subs({v: i.right}) for j in sols] + [i]),
                    {j.subs({v: i.right}) for j in eqns},
                )
            )
        if len(new_eqns) == 1:
            new_eqns = list(new_eqns[0])
        sols[:] = new_eqns
        return
    # Need a check for infinite solutions
    if eqn.left != v:
        raise ArithmeticError(f"Could not solve for {v}")
    # Substitute in the rest of equations
    ETSteps.register(ETSubNode(v, eqn.right))
    for i in range(len(sols)):
        sols[i] = sols[i].subs({v: eqn.right})
    for j in eqns.copy():
        eqns.remove(j)
        eqns.add(j.subs({v: eqn.right}))

    # # Put the newly solved equation at the end
    sols.append(eqn)


def _branched_solve(vals, sols):
    _, v = next_eqn(sols[0][1], vals)
    ETSteps.register(ETTextNode(f"Solve for {v}"))

    with ETSteps.branching(len(sols)) as branches:
        for idx in branches:
            data, eqns = sols[idx]
            data = list(data)
            eqn, _ = next_eqn(eqns, [v])
            if eqn.left == v:
                data.append(eqn)
                eqns.remove(eqn)
                sols[idx] = System(data), eqns
                continue
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            # ETSteps.register(ETNode(System({*sols[idx][0], *sols[idx][1]})))
            _solve(eqns, eqn, v, data)
            if data[0].__class__ is tuple:
                ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in data))
                sols.extend(data)
                sols[idx] = None
            else:
                sols[idx] = System(data), eqns
                ETSteps.register(ETNode(System({*data, *eqns})))
    # Flattening in case of double multiple solutions
    while True:
        for idx in range(len(sols)):
            if sols[idx] is None:
                sols.pop(idx)
                break
        else:
            break
    ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in sols))
    vals.remove(v)


def _foreach_solve(eqns, value):
    ETSteps.register(ETBranchNode(eqns))
    if not any(eqn.left != value for eqn in eqns):
        return eqns
    # Branched during the solving process
    sols = []
    with ETSteps.branching(len(eqns)) as branches:
        for idx, eqn in zip(branches, eqns):
            ETSteps.register(ETTextNode(f"Branch {idx+1}"))
            try:
                res = eqn.solve_for(value)
            except ArithmeticError as err:
                ETSteps.register(ETTextNode(repr(err), "#d7170b"))
                continue
            if res.__class__ is System:
                sols.extend(res)
            else:
                sols.append(res)
    return sols


class System(frozenset):
    """A system of equations"""

    def solve_for(self, vals: Sequence[Var]) -> System:
        if vals.__class__ is Var:
            return System(_foreach_solve(self, vals))

        ETSteps.register(ETTextNode("Solving for " + str(vals)[1:-1]))
        ETSteps.register(ETNode(self))
        # eqns = set(self)
        eqns = compute_grobner(self, list(vals))
        if not eqns:
            return System(eqns)
        if eqns != self:
            ETSteps.register(ETNode(System(eqns)))

        vals = set(vals)
        sols = []
        # Solve for each variable separately
        with ETSteps.branching(len(vals)) as branches:
            for _ in branches:
                # Branched solving: previous variable had multiple solutions
                if sols and sols[0].__class__ is tuple:
                    _branched_solve(vals, sols)
                    continue
                # Choose the easiest variable to isolate
                eqn, v = next_eqn(eqns, vals)
                ETSteps.register(ETTextNode(f"Solve for {v}"))
                _solve(eqns, eqn, v, sols)
                if sols[0].__class__ is tuple:
                    ETSteps.register(ETBranchNode(System({*i[0], *i[1]}) for i in sols))
                else:
                    ETSteps.register(ETNode(System({*sols, *eqns})))
                vals.remove(v)
        if isinstance(sols[0], tuple):
            sols = [i.simplify() for i, _ in sols]
        else:
            sols = [i.simplify() for i in sols]
        return System(sols)

    def __bool__(self) -> bool:
        return all(self)

    def __repr__(self) -> str:
        lpad = max(len(str(eqn.left)) for eqn in self)
        rpad = max(len(str(eqn.right)) for eqn in self)
        return print_system(
            [
                " " * (lpad - len(str(eqn.left)))
                + str(eqn)
                + " " * (rpad - len(str(eqn.right)))
                for eqn in sorted(self, key=lambda eqn: str(eqn.left))
            ]
        )

    def is_close(self, threshold: float = 1e-7):
        return all(eqn.is_close(threshold) for eqn in self)

    def expand(self):
        return System(i.expand() for i in self)

    def simplify(self):
        return System(i.simplify() for i in self)

    def subs(self, mapping: dict[Var, Node]) -> System:
        return System(i.subs(mapping) for i in self)

    def totex(self, align: bool = True) -> str:
        return "&" * align + "\\\\".join(map(lambda x: x.totex(align), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self) -> System:
        return System(i.normalize() for i in self)


__all__ = ["System"]
