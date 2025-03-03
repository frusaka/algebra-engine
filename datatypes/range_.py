from typing import Sequence

from .comparison import Comparison
from .collection import Collection
from utils import ineq_to_range


class Range(Collection):
    """A prettifier for inequality solutions"""

    def __new__(cls, ineqs: Sequence[Comparison], continuous=False):
        obj = super().__new__(cls, ineqs)
        object.__setattr__(obj, "continuous", continuous)
        return obj

    def __str__(self) -> str:
        ineq1, ineq2 = self
        if ineq1.rel.name.startswith("G"):
            ineq1, ineq2 = ineq2, ineq1
        left = ineq_to_range(ineq1)
        right = ineq_to_range(ineq2)
        if self.continuous:
            return right + ", " + left
        return " ∪ ".join(("(-∞, " + left, right + ", ∞)"))
