from __future__ import annotations
from typing import Sequence

from utils import difficulty_weight, print_system
from datatypes.eval_trace import *
from utils.analysis import next_eqn

from .collection import Collection
from .variable import Variable


class System(Collection):
    """A system of equations or inequalities"""

    def __getitem__(self, vals: Sequence[Variable]) -> System:
        """Solve for a system of (in)equalities"""
        from processing import subs

        # Assumeably from internal solving process
        if vals.__class__ is Variable:
            steps.register(ETBranchNode(self))
            return self
        vals = list(vals)
        seen = set()

        def solve(eqns, org, v):
            eqn = org[v]
            if eqn.__class__ is not self.__class__ and eqn.left.value != v:
                raise ArithmeticError(f"Could not solve for {v}")
            eqns.remove(org)
            if eqn.__class__ is System:
                seen.update(eqn)
                steps.register(ETSubNode(v, ETBranchNode(i.right for i in eqn)))
                new_eqns = []
                for i in eqn:
                    j = [subs(j, {v: i.right}) for j in eqns]
                    for idx in range(len(eqns)):
                        if eqns[idx] in seen:
                            seen.add(j[idx])
                    seen.add(i)
                    new_eqns.append(System(j + [i]))

                if len(new_eqns) == 1:
                    return list(new_eqns[0])
                return new_eqns
            seen.add(eqn)
            # Need a check for infinite solutions
            if eqn.left.value != v:
                return System(eqns + [eqn])
            # Substitute in the rest of equations
            steps.register(ETSubNode(v, eqn.right))
            for i in range(len(eqns)):
                was_seen = eqns[i] in seen
                eqns[i] = subs(eqns[i], {v: eqn.right})
                if was_seen:
                    seen.add(eqns[i])
            # Put the newly solved equation at the end
            eqns.append(eqn)
            return eqns

        eqns = list(self)
        steps.register(ETTextNode("Solving for " + str(vals)[1:-1]))
        steps.register(ETNode(self))
        # Solve for each variable separately
        with steps.branching(len(vals)) as branches:
            for _ in branches:
                if eqns[0].__class__ is System:
                    _, v = next_eqn([eqn for eqn in eqns[0] if not eqn in seen], vals)
                    steps.register(ETTextNode(f"Solve for {v}"))
                    with steps.branching(len(eqns)) as branches:
                        for idx in branches:
                            steps.register(ETTextNode(f"Branch {idx+1}"))
                            steps.register(ETNode(eqns[idx]))
                            data = list(eqns[idx])
                            eqn, _ = next_eqn([i for i in data if i not in seen], [v])
                            eqns[idx] = System(solve(data, eqn, v))
                            steps.register(ETBranchNode(eqns[idx]))
                    # Flatten when necessary (most cases)
                    if next(iter(next(iter(eqns)))).__class__ is System:
                        eqns = list(j for i in eqns for j in i)
                    steps.register(ETBranchNode(eqns))
                    vals.remove(v)
                    continue
                eqn, v = next_eqn([eqn for eqn in eqns if not eqn in seen], vals)
                steps.register(ETTextNode(f"Solve for {v}"))
                eqns = solve(eqns, eqn, v)
                if eqns.__class__ is System:
                    break
                if eqns[0].__class__ is System:
                    steps.register(ETBranchNode(eqns))
                else:
                    steps.register(ETNode(System(eqns)))
                vals.remove(v)
        seen.clear()
        return System(eqns)

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

    def approx(self, threshold: float = 1e-10):
        return all(eqn.approx(threshold) for eqn in self)

    def ast_subs(self, mapping: dict) -> frozenset:
        return frozenset(i.ast_subs(mapping) for i in self)

    def totex(self, align: bool = True) -> str:
        return "&" * align + "\\\\".join(map(lambda x: x.totex(align), self)).join(
            ("\\begin{cases}", "\\end{cases}")
        )

    def normalize(self, weaken=True) -> System:
        return System(i.normalize(weaken) for i in self)
