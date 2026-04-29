from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import copy
from dataclasses import dataclass
import inspect
from itertools import chain
from functools import update_wrapper
from enum import Enum
from typing import Any, Callable, Iterator, TypeVar, ParamSpec, Generic

import types
import weakref


from rich.text import Text
from rich.console import Group
from rich.panel import Panel
from rich.console import Group, Console
from rich.padding import Padding

from .constants import SYMBOLS
from .print_ import superscript, strip_ansi, colorize_ansi


def tex(value):
    return getattr(value, "totex", lambda: str(value))()


def delete_unused(idx):
    if type(idx) is int:
        if idx not in _steps:
            return
        step = _steps.pop(idx)
    else:
        step = idx
        if (idx := id(step.result)) in _steps:
            _steps.pop(idx)
    # # print("deleting", step)
    for i in step.children:
        delete_unused(i)
        # delete_unused(i)
    # step = _steps.pop(id(step.result))
    del step


def ref(value, force_keep=False, deletter_arg=None):
    if force_keep:
        return lambda: value
    try:
        weakref.finalize(value, delete_unused, id(value))
        return weakref.ref(value)
    except TypeError:
        return lambda: value


class OPArithmeticType(Enum):
    ADD = "#21ba3a"
    SUB = "#d7170b"
    DIV = "#ffc02b"
    MUL = "#0d80f2"
    POW = "#a219e6"
    SQRT = 6

    def tostr(self, a, b):
        color = self.value
        a = str(a).join("()") if a.__class__.__name__ in {"Step", "Add"} else str(a)
        b = str(b).join("()") if b.__class__.__name__ in {"Step", "Add"} else str(b)

        if self.name != "SQRT":
            return colorize_ansi(SYMBOLS.get(self.name), color).join("  ").join((a, b))
        color = OPArithmeticType.POW.value
        res = colorize_ansi("√", color) + a
        if b != "2":
            return superscript(b) + res
        return res

    def totex(self, a, b):
        color = self.value if self.name != "SQRT" else OPArithmeticType.POW.value
        color = "\\textcolor{" + color + "}"
        a = (
            tex(a).join(("\\left(", "\\right)"))
            if a.__class__.__name__ in {"Step", "Add"}
            else str(a)
        )
        b = (
            tex(b).join(("\\left(", "\\right)"))
            if b.__class__.__name__ in {"Step", "Add"}
            else tex(b)
        )

        if self.name == "SQRT":
            if b == "2":
                return color + "{\\sqrt{" + a + "}}"
            return color + "{\\sqrt[" + b + "]{" + a + "}}"
        if self.name == "POW":
            return color + "{{" + a + "}^" + b + "}"
        op = color + {"ADD": "+", "SUB": "-", "MUL": "\\times", "DIV": "\\div"}[
            self.name
        ].join("{}")
        return op.join((a, b))


class OPBinaryType(Enum):
    EQ = 0
    GT = 1
    GE = 2
    LT = 3
    LE = 4

    def tostr(self, left, right) -> str:
        return SYMBOLS.get(self.name).join("  ").join((str(left), str(right)))

    def totex(self, left, right) -> str:
        return "{}\\{} {}".format(tex(left), self.name.lower(), tex(right))


class OPSpecials(Enum):
    STATE = 0
    VERIFY = 1
    SUBS = 2
    SOLVE = 3
    HIDDEN = 4

    def tostr(self, *args) -> str:
        if self is OPSpecials.HIDDEN:
            return ""
        if self is OPSpecials.STATE:
            if len(args) == 1:
                return str(args[0])
            return str(args)
        if self is OPSpecials.VERIFY:
            return "verify" + str(args).replace(",)", ")")
        if self is OPSpecials.SOLVE:
            return "Solve for " + str(args[1])
        if self is OPSpecials.SUBS:
            return "Substitue {0} with {1}".format(
                colorize_ansi(str(args[0]), OPArithmeticType.SUB.value),
                colorize_ansi(str(args[1]), OPArithmeticType.ADD.value),
            )

    def totex(self, *args) -> str:
        if self is OPSpecials.HIDDEN:
            return ""
        if self is OPSpecials.STATE:
            if len(args) == 1:
                return tex(args[0])
            return tex(args)
        if self is OPSpecials.VERIFY:
            if len(args) == 1:
                return args[0].totex()
            return "verify" + ",".join(map(tex, args)).join("()")
        if self is OPSpecials.SOLVE:
            return "Solve for " + str(args[1])
        return "Substitue {0} with {1}".format(tex(args[0]), tex(args[1]))


@dataclass
class Step:
    type: str | OPArithmeticType | OPBinaryType | OPSpecials
    args: tuple
    result: Any = None
    reason: str = ""
    children: list[Step] = None
    changed: bool = True
    _options = dict(
        chain(
            OPArithmeticType.__members__.items(),
            OPBinaryType.__members__.items(),
            OPSpecials.__members__.items(),
        )
    )

    def __init__(
        self,
        id: str,
        args: tuple,
        result: Any = None,
        reason: str = "",
        children: list[Step] = None,
        changed: bool = True,
        force_keep: bool = False,
    ) -> None:
        if t := self._options.get(id, None):
            self.type = t
            if self.type is OPSpecials.VERIFY:
                result = "❌✅📉"[result]
        else:
            self.type = id
        if not hasattr(args, "__iter__"):
            args = (args,)
        self.args = list(args)
        self._result = ref(result, force_keep and changed, self)
        self.children = children or []
        self.reason = reason
        self.changed = changed

    def __copy__(self):
        return Step(
            self.type,
            self.args.copy(),
            self.result,
            self.reason,
            self.children.copy(),
            self.changed,
        )

    @property
    def result(self):
        return self._result()

    def force_keep(self):
        if not self.changed:
            return
        res = self.result
        self._result = lambda: res

    def __str__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(*self.args)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + ", ".join(map(str, self.args)).join("()")

    def header(self):
        if self.type is OPSpecials.STATE:
            return str(self)
        return str(self) + " ⟶ " + str(self.result)

    def totex(self) -> str:
        if type(self.type) is not str:
            return self.type.totex(*self.args)
        if len(self.args) == 1:
            return "\\mathrm{" + self.type + "}" + tex(self.args[0]).join("()")
        return "\\mathrm{" + self.type + "}" + ",".join(map(tex, self.args)).join("()")

    def tex_header(self) -> str:
        if self.type is OPSpecials.STATE:
            return self.totex()
        return self.totex() + "\\longrightarrow " + tex(self.result)

    def __rich_console__(self, console: Console, *_) -> Iterator[Text | Panel]:
        def rich(step: Step, depth, index):
            width = console.width - 3 - depth * 4
            idx = str(index) + ". " if index else ""
            lpad = bool(depth) + 1
            label = step.reason + ": " if step.reason else ""
            if not step.children:
                res = Text.from_ansi(f"{idx}{label}{step.header()}")
                res.pad_left(lpad)
                if depth:
                    res.truncate(width, overflow="ellipsis")
                return res
            p = len(step.children) > 1
            lpad *= not len(step.children) or not bool(index) or not depth
            title = idx + label
            if step.result is not None:
                title += str(step)
            res = Group(
                Text.from_ansi(title),
                Padding(
                    Group(
                        *(
                            rich(i, depth + 1, idx if p else 0)
                            for idx, i in enumerate(step.children, 1)
                        )
                    ),
                    (0, 0, 0, lpad),
                ),
                Text(f"Result: {step.result}" if step.result is not None else ""),
            )
            if not res.renderables[-1]:
                res.renderables.pop()
            elif depth:
                res.renderables[0].pad_left(lpad)
                res.renderables[0].truncate(width, overflow="ellipsis")
                res.renderables[-1].pad_left(lpad + 2)
                res.renderables[-1].truncate(width, overflow="ellipsis")
            if depth == 0 or step.children and index and step.result is not None:
                return Panel(res, expand=False)
            return res

        return iter((rich(self, 0, 0),))

    def toJSON(self):
        def json(step: Step):
            label = step.reason + ": " if step.reason else ""
            delims = ("$$", "$$") if not label else ("\\(", "\\)")
            if not step.children:
                return label + step.tex_header().join(delims)
            res = [
                label + (step.totex().join(delims) if step.result is not None else ""),
                [json(i) for i in step.children],
                (
                    f"Result: \\({tex(step.result)}\\)"
                    if step.result is not None
                    else ""
                ),
            ]
            if not res[-1]:
                res.pop()
            return res

        return json(self)


def set_verbosity(value: bool) -> None:
    global _verbose
    _verbose = value


def verbose() -> bool:
    return _verbose


def register(step: Step | Any, scoped=True, reason=None, deduplicate=True) -> None:
    if not _verbose or scoped and _curr_hist.get() is None:
        return
    if type(step) is not Step:
        step = _steps.get(id(step), None)
        if step:
            if not step.changed and not step.children:
                return
    if step is None:
        return
    if reason is not None:
        step.reason = reason

    if scoped:
        if (ctx := _curr_hist.get()) is None:
            return
        if step.changed or step.children:
            ctx.append(step)
        if step.result is not None:
            step.force_keep()
        # To be revised
        if deduplicate and (idx := id(step.result)) in _steps:
            _steps.pop(idx)
    else:
        _steps[id(step.result)] = step


@contextmanager
def scoped(scope: list):
    ctx = _curr_hist.set(scope)
    try:
        yield
    finally:
        _curr_hist.reset(ctx)


P = ParamSpec("P")
R = TypeVar("R")


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
        history = []
        with scoped(history):
            result = self.func(*args, **kwargs)
        if not _verbose:  # or not (changed := self._is_simplified(result, args)):
            return result
        if len(args) == 1 and result == args[0]:
            return args[0]
        result = copy(result)
        _steps[id(result)] = Step(
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


def explain(expr, default=True) -> Step | Any:
    if not (res := _steps.get(id(expr), None)):
        return expr if default else None
    op = copy(res)
    n = len(res.children)

    for idx, i in enumerate(res.args):
        if not (v := explain(i, False)):
            continue
        res.args[idx] = v
        res.children.insert(idx, v)
        _steps.pop(id(v.result))

    if len(res.children) > n and not n:
        res.children.append(op)
    if not res.changed and not res.children:
        return expr if default else None
    return res


_steps: dict[int, Step] = {}
_verbose: bool = False
_curr_hist = ContextVar("_curr_hist", default=None)


__all__ = ["Step"]
