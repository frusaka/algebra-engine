from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import copy
import inspect
from functools import update_wrapper
from typing import Any, Callable, TypeVar, ParamSpec, Generic

import types
from . import step

P = ParamSpec("P")
R = TypeVar("R")


@contextmanager
def scoped(scope: list):
    ctx = _curr_hist.set(scope)
    try:
        yield
    finally:
        _curr_hist.reset(ctx)


def register(
    value: step.Step | Any, scoped=True, reason=None, deduplicate=True
) -> None:
    if not step._verbose or scoped and _curr_hist.get() is None:
        return
    if type(value) is not step.Step:
        value = step._explain(value)
        # value = step._steps.get(id(value), None)
        if value:
            if not value.changed and not value.children:
                return
    if value is None:
        return
    if reason is not None:
        value.reason = reason

    if scoped:
        if (ctx := _curr_hist.get()) is None:
            return
        if value.changed or value.children:
            ctx.append(value)
        if value.result is not None:
            value.force_keep()
        # To be revised
        if deduplicate and (idx := id(value.result)) in step._steps:
            step._steps.pop(idx)
    else:
        step._steps[id(value.result)] = value


class Tracked(Generic[P, R]):
    def __init__(
        self,
        func: Callable[P, R],
        id: str = None,
        label: str = None,
    ):
        id = id if id is not None else func.__name__
        label = label if label is not None else ""
        self.func = func  # lru_cache(maxsize=500)(func)
        self.id = id
        self.label = label
        update_wrapper(self, func)
        self.__signature__ = inspect.signature(func)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        if not step._verbose:
            return self.func(*args, **kwargs)
        with scoped(history := []):
            result = self.func(*args, **kwargs)
            if (v := step._steps.get(id(result))) and v.changed:
                register(result)
        if len(args) == 1 and result == args[0]:
            return args[0]
        result = copy(result)
        step._steps[id(result)] = step.Step(
            self.id,
            args,
            result,
            self.label,
            history,
            changed=self._is_simplified(result, args),
        )
        return result

    # __call__ = lru_cache(maxsize=1 << 40)(__call__)

    def check_changed(self, fn):
        self._is_simplified = fn
        return fn

    @staticmethod
    def _is_simplified(result, args):
        if len(args) == 1:
            return result != args[0]
        return True


def tracked(id: str = None, label: str = None):
    def wrapper(func: Callable[P, R]) -> Tracked[P, R]:
        return Tracked(func, id, label)

    return wrapper


_curr_hist = ContextVar("_curr_hist", default=None)

__all__ = ["tracked", "register", "scoped"]
