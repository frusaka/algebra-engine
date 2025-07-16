from __future__ import annotations

from dataclasses import dataclass
from .eval_trace import *

from datatypes.base import Node


@dataclass(frozen=True, slots=True)
class Interval:
    """A prettifier for inequality solutions"""

    start: int | None
    end: int | None
    open: tuple[bool]

    def __repr__(self) -> str:
        if self.start is not None:
            start = "[("[self.open[0]] + str(self.start)
        else:
            start = "(-∞"
        if self.end is not None:
            end = str(self.end) + "])"[self.open[1]]
        else:
            end = "∞)"
        return ", ".join((start, end))

    def __contains__(self, other: Node) -> bool:
        left = self.start.approx() if self.start is not None else float("-inf")
        right = self.end.approx() if self.end is not None else float("inf")
        other = other.approx()
        left_oper = other.__gt__ if self.open[0] else other.__ge__
        right_oper = other.__lt__ if self.open[1] else other.__le__
        return left_oper(left) and right_oper(right)

    def intersect(self, other: Interval) -> Interval | None:
        from .core import to_float

        left = max(self.start, other.start, key=to_float)
        right = min(self.end, other.end, key=lambda x: to_float(x, 1))
        # If no overlap
        if to_float(left) > to_float(right, 1):
            return

        # If touching at a single point, only include if it's closed on both sides
        if left == right:
            left_included = (self.start == left and not self.open[0]) and (
                other.start == left and not other.open[0]
            )
            right_included = (self.end == right and not self.open[1]) and (
                other.end == right and not other.open[1]
            )
            if not (left_included or right_included):
                return

        left_open = self.open[0] if self.start == left else other.open[0]
        right_open = self.open[1] if self.end == right else other.open[1]

        return Interval(left, right, open=(left_open, right_open))

    def totex(self) -> str:
        start = "\\left"
        if self.start is not None:
            start += "[("[self.open[0]] + self.start.totext()
        else:
            start += "-\\infty"
        if self.end is not None:
            end = str(self.end) + "\\right" + "])"[self.open[1]]
        else:
            end = "\\infty\\right)"
        return ",".join((start, end))


INF = Interval(None, None, (True, True))
