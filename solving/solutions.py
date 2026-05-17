from itertools import zip_longest
from datatypes.base import Expr
from .interval import Interval


class SolutionSet(frozenset):
    def __repr__(self):
        if not self:
            return "∅"
        data = [str(i).split("\n") for i in self]
        n = len(max(data, key=len))
        return "\n".join(
            (", " if idx == n else "  ").join(items)
            for idx, items in enumerate(zip_longest(*data, fillvalue=""), 1)
        ).join("{}")

    def totex(self) -> str:
        if not self:
            return "\\emptyset"
        return ",".join(
            (
                i.totex()
                if i.__class__ is not tuple
                else ",".join(map(lambda x: x.totex(), i)).join(("\\left(", "\\right)"))
            )
            for i in self
        ).join(("\\left\\lbrace ", "\\right\\rbrace "))


class IntervalUnion(tuple):
    def __repr__(self) -> str:
        return " ∪ ".join(map(str, self))

    def totex(self) -> str:
        return "\\cup".join(i.totex() for i in self)

    def __contains__(self, other):
        if isinstance(other, Expr):
            return any(other in interval for interval in self)

        elif isinstance(other, Interval):
            return any(other in interval for interval in self)

        else:
            return NotImplemented


__all__ = ["SolutionSet", "IntervalUnion"]
