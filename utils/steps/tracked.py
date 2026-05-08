from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import copy
import inspect
from functools import update_wrapper
from typing import Any, Callable, TypeVar, ParamSpec, Generic

import types
from . import step as steps

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
    step: steps.Step | Any, scoped=True, reason=None, deduplicate=True, scope=None
) -> None:
    if not steps._verbose or scoped and _curr_hist.get() is None:
        return
    if type(step) is not steps.Step:
        step = steps._explain(step)
        # step = steps._steps.get(id(step), None)
        if step:
            if not step.changed and not step.children:
                return
    if step is None:
        return
    if reason is not None:
        step.reason = reason

    ctx = scope if scope is not None else _curr_hist.get()
    if scoped and ctx is not None:
        if step.changed or step.children:
            ctx.append(step)
            if step.result is not None:
                step.force_keep()
        # To be revised
        if deduplicate and (idx := id(step.result)) in steps._steps:
            steps._steps.pop(idx)
    else:
        steps._steps[id(step.result)] = step


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
        if not steps._verbose:
            return self.func(*args, **kwargs)
        scope = _curr_hist.get()
        with scoped(history := []):
            try:
                result = self.func(*args, **kwargs)
                if steps._steps.get(id(result)):
                    register(result)
            except Exception as e:
                step = steps.Step(self.id, args, e, self.label, history)
                steps._steps[id(e)] = step
                if scope is not None:
                    register(e, scope=scope)
                raise
        if len(args) == 1 and result == args[0]:
            return args[0]
        result = copy(result)
        steps._steps[id(result)] = steps.Step(
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
