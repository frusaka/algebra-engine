from __future__ import annotations

import itertools
import operator
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import lru_cache, partial, reduce
import utils
from utils.steps import ETOperator, Step
from utils import steps

from . import nodes


from typing import TYPE_CHECKING, Generator, Iterable

if TYPE_CHECKING:
    from solving.comparison import Comparison
    from .const import Const


class Node:
    @steps.tracked("ADD")
    def __add__(self, other) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Add(self, other)

    @__add__.check_changed
    def _add_changed(result, args):
        # print(result, args, tuple(itertools.chain(*map(nodes.Add.flatten, args))))
        return not isinstance(result, nodes.Add) or len(result.args) < len(
            tuple(itertools.chain(*map(nodes.Add.flatten, args)))
        )

    def __radd__(self, other) -> Node:
        return nodes.Const(other) + self

    @steps.tracked("SUB")
    def __sub__(self, other) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Add(self, nodes.Mul(other, nodes.Const(-1), distr_const=True))

    __sub__.check_changed(_add_changed)

    def __rsub__(self, other) -> Node:
        return nodes.Const(other) - self

    @steps.tracked("MUL")
    def __mul__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Mul(self, other)

    @__mul__.check_changed
    def _mul_changed(result, args):
        return not isinstance(result, nodes.Mul) or len(result.args) < len(
            list(itertools.chain(*map(nodes.Mul.flatten, args)))
        )

    def __rmul__(self, other) -> Node:
        return self * other

    @steps.tracked("DIV")
    def __truediv__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Mul(self, nodes.Pow(other, nodes.Const(-1)))

    __truediv__.check_changed(_mul_changed)

    def __rtruediv__(self, other):
        return nodes.Const(other) / self

    @steps.tracked("POW")
    def __pow__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Pow(self, other)

    @__pow__.check_changed
    def _(result, args) -> bool:
        return (
            args[0] != 0
            and args[1] != 0
            and (result.__class__ is not nodes.Pow or (result.base, result.exp) != args)
        )

    def __rpow__(self, other) -> Node:
        return nodes.Const(other) ** self

    def __neg__(self) -> Node:
        return self * -1

    def __pos__(self) -> Node:
        return self

    def __contains__(self, value: Node) -> bool:
        return value in str(self)

    def multiply(self, other: Node) -> Node:
        if other.__class__ is nodes.Add:
            return other.multiply(self)
        return self * other

    def divide(self, other: Node) -> Node:
        return self * other**-1

    @steps.tracked()
    def factor(self) -> Node:
        return utils.factor(self)

    def _expand(self):
        return self

    @steps.tracked()
    def expand(self) -> Node:
        return self._expand()

    def canonical(self) -> tuple[Const, Node]:
        return nodes.Const(1), self

    def as_ratio(self) -> tuple[Node]:
        return (self, nodes.Const(1))

    @steps.tracked()
    def subs(self, mapping: dict[Node]) -> Node:
        @lru_cache
        def _subs(n):
            if isinstance(n, nodes.Number):
                return n
            if (v := mapping.get(n, None)) is not None:
                steps.register(Step("", ETOperator("", (n,), v)))
                return v
            if type(n) is nodes.Var:
                return n
            if type(n) is nodes.Pow:
                res = _subs(n.base) ** _subs(n.exp)
                steps.register(res)
                return res

            args = [_subs(i) for i in n]
            op = Node.__add__ if type(n) is nodes.Add else Node.__mul__
            res = reduce(op, args)
            steps.register(res)
            return res

        return _subs(self)

    @subs.check_changed
    def _(result, args):
        return result != args[0]

    @steps.tracked("approximate")
    def approx(self) -> float | complex:
        return self._approx()

    def totex(self) -> str:
        return str(self)


@dataclass(frozen=True, init=False, slots=True)
class Collection(ABC, Node):
    args: tuple[Node]

    @lru_cache
    def __new__(cls, *args: Node, **kwargs) -> Node:
        return cls.from_terms(args, **kwargs)

    if TYPE_CHECKING:

        def __init__(self, *args: Node, **kwargs): ...

    def __hash__(self) -> int:
        return self._hash

    def __iter__(self):
        return iter(self.args)

    def __copy__(self):
        cls = type(self)
        obj = super(Collection, cls).__new__(cls)
        object.__setattr__(obj, "args", self.args)
        object.__setattr__(obj, "_hash", self._hash)
        return obj

    @classmethod
    def from_terms(cls, args: Iterable[Node], modify=True, **kwargs) -> Node:
        # args = itertools.chain(*map(cls.flatten, args))
        if modify:
            args = cls.merge(
                itertools.chain(
                    *map(
                        partial(
                            cls.flatten, factor=not kwargs.get("distr_const", False)
                        ),
                        args,
                    )
                ),
                **kwargs,
            )
        if len(args) == 1:
            return args.pop()
        obj = super(Collection, cls).__new__(cls)
        object.__setattr__(obj, "args", tuple(args))
        object.__setattr__(obj, "_hash", hash((cls, obj.args)))
        return obj

    @classmethod
    def flatten(cls, node: Node, factor=True) -> Generator[Node, None, None]:
        if node.__class__ is cls:
            yield from node.args
        elif factor and cls is nodes.Mul and node.__class__ is nodes.Add:
            c, v = node.cancel_gcd()
            if c != 1:
                yield from cls.flatten(c)
            yield v
        else:
            yield node

    @classmethod
    @abstractmethod
    def merge(cls, args: Iterable[Node]) -> list[Node]:
        pass

    @staticmethod
    @abstractmethod
    def sort_terms(args: Iterable[Node]) -> list[Node]:
        pass

    def _approx(self) -> float | complex:
        op = self.__class__.__name__.lower()
        return reduce(getattr(operator, op), (i._approx() for i in self))


__all__ = ["Node", "Collection"]
