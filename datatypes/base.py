from __future__ import annotations

from copy import copy
import itertools
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import partial, reduce
import operator
import utils
from utils import steps

from . import expr


from typing import TYPE_CHECKING, Generator, Iterable

if TYPE_CHECKING:
    from .const import Const, Float


class Expr:
    def __copy__(self):
        cls = type(self)
        obj = object.__new__(cls)
        for s in cls.__slots__:
            object.__setattr__(obj, s, getattr(self, s))
        return obj

    @steps.tracked("ADD")
    def __add__(self, other) -> Expr:
        if not isinstance(other, Expr):
            other = expr.Const(other)
        return expr.Add(self, other)

    @__add__.check_changed
    def _add_changed(result, args):
        return not any(n == 0 for n in args) and (
            not isinstance(result, expr.Add)
            or len(result.args)
            < len(tuple(itertools.chain(*map(expr.Add.flatten, args))))
        )

    def __radd__(self, other) -> Expr:
        return expr.Const(other) + self

    @steps.tracked("SUB")
    def __sub__(self, other) -> Expr:
        if not isinstance(other, Expr):
            other = expr.Const(other)
        return expr.Add(self, expr.Mul(other, expr.Const(-1), distr_const=True))

    __sub__.check_changed(_add_changed)

    def __rsub__(self, other) -> Expr:
        return expr.Const(other) - self

    @steps.tracked("MUL")
    def __mul__(self, other: Expr) -> Expr:
        if not isinstance(other, Expr):
            other = expr.Const(other)
        return expr.Mul(self, other)

    @__mul__.check_changed
    def _mul_changed(result, args):
        return not any(n == 1 for n in args) and (
            not isinstance(result, expr.Mul)
            or len(result.args)
            < len(list(itertools.chain(*map(expr.Mul.flatten, args))))
        )

    def __rmul__(self, other) -> Expr:
        return self * other

    @steps.tracked("DIV")
    def __truediv__(self, other: Expr) -> Expr:
        if not isinstance(other, Expr):
            other = expr.Const(other)
        if other == 0:
            raise ZeroDivisionError(f"{self} / {other}")
        return expr.Mul(self, expr.Pow(other, expr.Const(-1)))

    __truediv__.check_changed(_mul_changed)

    def __rtruediv__(self, other):
        return expr.Const(other) / self

    @steps.tracked("POW")
    def __pow__(self, other: Expr) -> Expr:
        if not isinstance(other, Expr):
            other = expr.Const(other)
        return expr.Pow(self, other)

    @__pow__.check_changed
    def _(result, args) -> bool:
        return (
            args[0] not in (0, 1)
            and args[1] != 0
            and (result.__class__ is not expr.Pow or (result.base, result.exp) != args)
        )

    def __rpow__(self, other) -> Expr:
        return expr.Const(other) ** self

    def __neg__(self) -> Expr:
        return self * -1

    def __pos__(self) -> Expr:
        return self

    def __contains__(self, value: Expr) -> bool:
        return value in str(self)

    def multiply(self, other: Expr) -> Expr:
        if other.__class__ is expr.Add:
            return other.multiply(self)
        return self * other

    def divide(self, other: Expr) -> Expr:
        return self * other**-1

    def factor(self) -> Expr:
        return utils.factor(self)

    def _expand(self):
        return self

    @steps.tracked()
    def expand(self) -> Expr:
        return self._expand()._expand()

    def canonical(self) -> tuple[Const, Expr]:
        return expr.Const(1), self

    def as_ratio(self) -> tuple[Expr]:
        return (self, expr.Const(1))

    @steps.tracked()
    def subs(self, mapping: dict[Expr]) -> Expr:
        if isinstance(self, expr.Number):
            return self
        if (v := mapping.get(self, None)) is not None:
            return v
        if type(self) is expr.Var:
            return self
        if type(self) is expr.Pow:
            return self.base.subs(mapping=mapping) ** self.exp.subs(mapping=mapping)

        args = [i.subs(mapping=mapping) for i in self]
        op = Expr.__add__ if type(self) is expr.Add else Expr.__mul__
        return reduce(op, args)
        steps.register(res)
        return res

    @subs.check_changed
    def _(result, args):
        return result != args[0]

    def _approx(self) -> float | complex:
        raise NotImplementedError(
            f"Approximation not implemented for {type(self).__name__}"
        )

    @steps.tracked("approximate")
    def approx(self) -> Float:
        return expr.Float(self._approx())

    def totex(self) -> str:
        return str(self)


@dataclass(frozen=True, init=False)
class Collection(ABC, Expr):
    args: tuple[Expr]
    __slots__ = ("args", "_hash")

    @utils.lru_cache
    def __new__(cls, *args: Expr, **kwargs) -> Expr:
        return cls.from_terms(args, **kwargs)

    if TYPE_CHECKING:

        def __init__(self, *args: Expr, **kwargs): ...

    def __hash__(self) -> int:
        return self._hash

    def __iter__(self):
        return iter(self.args)

    @classmethod
    def from_terms(cls, args: Iterable[Expr], modify=True, **kwargs) -> Expr:
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
    def flatten(cls, node: Expr, factor=True) -> Generator[Expr, None, None]:
        if node.__class__ is cls:
            yield from node.args
        elif factor and cls is expr.Mul and node.__class__ is expr.Add:
            c, v = node.cancel_gcd()
            if c != 1:
                yield from cls.flatten(c)
            yield v
        else:
            yield node

    @classmethod
    @abstractmethod
    def merge(cls, args: Iterable[Expr]) -> list[Expr]:
        pass

    @staticmethod
    @abstractmethod
    def sort_terms(args: Iterable[Expr]) -> list[Expr]:
        pass

    def _approx(self) -> float | complex:
        return reduce(
            getattr(operator, self.__class__.__name__.lower()),
            (i._approx() for i in self),
        )


__all__ = ["Expr", "Collection"]
