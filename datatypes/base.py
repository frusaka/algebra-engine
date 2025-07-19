from __future__ import annotations

import itertools
import operator
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import lru_cache, reduce

from . import nodes


from typing import TYPE_CHECKING, Generator, Iterable

if TYPE_CHECKING:
    from .var import Var
    from .const import Const


class Node:
    def __add__(self, other) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Add(self, other)

    def __radd__(self, other) -> Node:
        return nodes.Add(nodes.Const(other), self)

    def __sub__(self, other) -> Node:
        return self + other * -1

    def __rsub__(self, other) -> Node:
        return nodes.Add(nodes.Const(other), self * -1)

    def __mul__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        if self.__class__ is nodes.Const and other.__class__ is not nodes.Const:
            self, other = other, self
        if self.__class__ is nodes.Add and other.__class__ is nodes.Const:
            return self.multiply(other)
        return nodes.Mul(self, other)

    def __rmul__(self, other) -> Node:
        return self * other

    def __truediv__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return self * other**-1

    def __rtruediv__(self, other):
        return nodes.Const(other) / self

    def __pow__(self, other: Node) -> Node:
        if not isinstance(other, Node):
            other = nodes.Const(other)
        return nodes.Pow(self, other)

    def __rpow__(self, other) -> Node:
        return nodes.Pow(nodes.Const(other), self)

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

    def simplify(self) -> Node:
        return self

    def expand(self) -> Node:
        return self

    def canonical(self) -> tuple[Const, Node]:
        return nodes.Const(1), self

    def as_ratio(self) -> tuple[Node]:
        return (self, nodes.Const(1))

    def subs(self, mapping: dict[Var, Node]) -> Node:
        return mapping.get(self, self)

    def totex(self) -> str:
        return str(self)


@dataclass(frozen=True, init=False, slots=True)
class Collection(ABC, Node):
    args: frozenset[Node]

    @lru_cache
    def __new__(cls, *args: Node) -> Node:
        return cls.from_terms(args)

    if TYPE_CHECKING:

        def __init__(self, *args: Node): ...

    def __hash__(self) -> int:
        return self._hash

    def __iter__(self):
        return iter(self.args)

    @classmethod
    def from_terms(cls, args: Iterable[Node], modify=True) -> Node:
        if modify:
            args = cls.merge(itertools.chain(*map(cls.flatten, args)))
        if len(args) == 1:
            return args.pop()
        obj = super(Collection, cls).__new__(cls)
        object.__setattr__(obj, "args", frozenset(args))
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

    def subs(self, mapping: dict[Var, Node]) -> Node:
        return self.__class__.from_terms(node.subs(mapping) for node in self)

    def approx(self) -> float | complex:
        op = self.__class__.__name__.lower()
        return reduce(getattr(operator, op), (i.approx() for i in self))


__all__ = ["Node", "Collection"]
