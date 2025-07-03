from datatypes.base import Node
from .interval import Interval


class SolutionSet(frozenset):
    def __repr__(self):
        if not self:
            return "∅"
        return ", ".join(str(i) for i in self).join("{}")


class IntervalUnion(tuple):
    def __repr__(self) -> str:
        return " ∪ ".join(map(str, self))

    def totex(self) -> str:
        return "\\cup".join(i.totex() for i in self)

    def __contains__(self, other):
        if isinstance(other, Node):
            return any(other in interval for interval in self)

        elif isinstance(other, Interval):
            return any(other in interval for interval in self)

        else:
            return NotImplemented


__all__ = ["SolutionSet", "IntervalUnion"]
