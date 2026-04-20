from __future__ import annotations

from contextlib import contextmanager
from copy import copy
from dataclasses import dataclass, field
import inspect
from itertools import chain, zip_longest
from functools import lru_cache, partial, update_wrapper, wraps
from enum import Enum
from typing import Any, Callable, Iterator, TypeVar, ParamSpec, Generic

import types


from rich.text import Text
from rich.console import Group
from rich.panel import Panel
from rich.console import Group, Console
from rich.padding import Padding

from .constants import SYMBOLS
from .print_ import superscript, strip_ansi, colorize_ansi


class ETNode:
    def __init__(self, result):
        self.args = (result,)
        self.result = result

    def header(self):
        return str(self.result)

    def __repr__(self):
        return ""

    def totex(self):
        return self.result.totex()

    def torich(self, depth):
        res = [Text.from_ansi(i) for i in str(self).split("\n")]
        [t.truncate(80 - 4 * depth, overflow="ellipsis") for t in res]
        if len(res) == 1:
            return res[0]
        return Group(*res)


class OPArithmeticType(Enum):
    ADD = "#21ba3a"
    SUB = "#d7170b"
    DIV = "#ffc02b"
    MUL = "#0d80f2"
    POW = "#a219e6"
    SQRT = 6

    def tostr(self, a, b):
        color = self.value
        a = (
            str(a).join("()")
            if a.__class__.__name__ in {"ETOperator", "Add"}
            else str(a)
        )
        b = (
            str(b).join("()")
            if b.__class__.__name__ in {"ETOperator", "Add"}
            else str(b)
        )

        if self.name != "SQRT":
            return colorize_ansi(SYMBOLS.get(self.name), color).join("  ").join((a, b))
        color = OPArithmeticType.POW.value
        res = colorize_ansi("√", color) + a
        if b != "2":
            return superscript(b) + res
        return res

    def totex(self, value):
        color = self.value if self.name != "SQRT" else OPArithmeticType.POW.value
        color = "\\textcolor{" + color + "}"
        if self.name == "SQRT":
            if value == 2:
                return color + "{\\sqrt{\\phantom{a}}}"
            return color + (f"\\sqrt[{value}]" + "{\\phantom{a}}").join("{}")
        if self.name == "POW":
            return color + ("(\\phantom{a})^" + str(value)).join("{}")
        if value.__class__.__name__ == "Add":
            value = value.totex().join(("\\left(", "\\right)"))
        else:
            value = value.totex()
        if self.name == "ADD":
            return color + ("+" + value).join("{}")
        if self.name == "SUB":
            return color + ("-" + value).join("{}")
        if self.name == "MUL":
            return color + ("\\times" + value.join("{}")).join("{}")
        if self.name == "DIV":
            return color + ("\\div" + value.join("{}")).join("{}")


class OPBinaryType(Enum):
    EQ = 0
    GT = 1
    GE = 2
    LT = 3
    LE = 4

    def tostr(self, left, right):
        return SYMBOLS.get(self.name).join("  ").join((str(left), str(right)))


class OPSpecials(Enum):
    VERIFY = 0
    SUBS = 1

    def tostr(self, *args) -> str:
        if self is OPSpecials.VERIFY:
            if len(args) == 1:
                return str(args[0])
            return "verify" + str(args)
        return f"Substitue {args[0]} with {args[1]}"


class ETOperator(ETNode):
    _options = dict(
        chain(
            OPArithmeticType.__members__.items(),
            OPBinaryType.__members__.items(),
            OPSpecials.__members__.items(),
        )
    )

    def __init__(self, id: str, args: tuple[ETNode], result: Any) -> None:
        if t := self._options.get(id, None):
            self.type = t
            if self.type is OPSpecials.VERIFY:
                result = "❌✅📉"[result]
        else:
            self.type = id
        self.args = list(args)
        self.result = result

    def __repr__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(*self.args)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + str(tuple(self.args))

    def header(self):
        return str(self) + " --> " + str(self.result)


class ETBranch(ETNode):
    def __init__(self, result):
        self.args = list(result)
        if self.args[0].__class__.__name__ == "Comparison":
            self.args.sort(key=str)

    def header(self):
        if self.args[0].__class__.__name__ != "System":
            return ",  ".join(map(str, self.args))
        data = [str(i).split("\n") for i in self.args]
        return "\n".join(
            "    ".join(items) for items in zip_longest(*data, fillvalue="")
        )

    @property
    def result(self):
        return self.header()

    def totex(self):
        return ",\\quad ".join(i.totex() for i in self.result)


@dataclass
class Step:
    label: str
    transform: ETOperator | ETNode
    children: list[Step] = field(default_factory=list)
    changed: bool = True

    def __repr__(self) -> str:
        def _str(step, depth):
            if not step.children:
                return f"{step.label}: {step.transform}"
            res = f"{step.label}: {step.transform}"
            for idx, i in enumerate(step.children, 1):
                res += "\n" + "   " * depth + str(idx) + ". " + _str(i, depth + 1)
            res += "\n" + "   " * depth + str(idx + 1) + f". Final: {step.result}"
            return res

        return _str(self, 1)

    def __rich_console__(self, console: Console, *_) -> Iterator[Text | Panel | Group]:
        def rich(step, depth, index):
            width = console.width - 3 - depth * 4
            idx = str(index) + ". " if index else ""
            lpad = depth + 1
            label = step.label + ": " if step.label else ""
            if not step.children:
                res = Text.from_ansi(f"{idx}{label}{step.transform.header()}")
                res.pad_left(lpad)
                res.truncate(width, overflow="ellipsis")
                return res
            p = len(step.children) > 1
            lpad *= not len(step.children) or not bool(index) or not depth
            res = Group(
                Text.from_ansi(f"{idx}{label}{step.transform}"),
                Padding(
                    Group(
                        *(
                            rich(i, 1, idx if p else 0)
                            for idx, i in enumerate(step.children, 1)
                        )
                    ),
                    (0, 0, 0, lpad),
                ),
                Text(
                    f"Result: {step.transform.result}"
                    if type(self.transform) is not ETNode
                    else ""
                ),
            )
            res.renderables[0].pad_left(lpad)
            res.renderables[0].truncate(width, overflow="ellipsis")
            if len(res.renderables[-1]):
                res.renderables[-1].pad_left(lpad + 2)
                res.renderables[-1].truncate(width, overflow="ellipsis")
            else:
                res.renderables.pop()
            if depth == 0 or step.children and index:
                return Panel(res, expand=False)
            return res

        return iter((rich(self, 0, 0),))


def set_verbosity(value: bool) -> None:
    global _verbose
    _verbose = value


def verbose() -> bool:
    return _verbose


def register(step: Step | Any, scoped=True) -> None:
    if not _verbose or scoped and _curr_hist is None:
        return
    if step is not None and type(step) is not Step:
        step = _steps.get(id(step), None)
        if step and not step.changed and not step.children:
            return
    if step is None:
        return
    if scoped:
        _curr_hist.append(step)
    else:
        _steps[id(step.transform.result)] = step


@contextmanager
def scoped(scope: list):
    global _curr_hist
    before = _curr_hist
    _curr_hist = scope
    try:
        yield
    finally:
        _curr_hist = before


P = ParamSpec("P")
R = TypeVar("R")


class Tracked(Generic[P, R]):
    def __init__(self, func: Callable[P, R], id: str = None, label: str = None):
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
        if not _verbose:
            return result
        changed = self._is_simplified(result, args)
        if not changed and len(args) == 1 and result == args[0]:
            return args[0]
        result = copy(result)
        _steps[id(result)] = Step(
            self.label,
            ETOperator(self.id, args, result),
            history,
            changed,
        )
        return result

    # __call__ = lru_cache(maxsize=1 << 40)(__call__)

    def check_changed(self, fn):
        self._is_simplified = fn
        return fn

    def register(self, expr):
        if not _verbose or _curr_hist is None:
            return
        step = _steps.get(id(expr))
        if step is None:
            return
        self.steps.append(step)

    @staticmethod
    def _is_simplified(result, args):
        if len(args) == 1:
            return result != args[0]
        return True

    def fallback(self, fn):
        self._fallbcak = fn
        return fn

    @staticmethod
    def _fallback(result, args):
        return result


def tracked(id: str = None, label: str = ""):
    def wrapper(func: Callable[P, R]) -> Tracked[P, R]:
        return Tracked(func, id, label)

    return wrapper


def explain(expr, default=True) -> Step | Any:
    if not (res := _steps.get(id(expr), None)):
        return expr if default else None

    op = copy(res.transform)
    op.args = op.args.copy()
    n = len(res.children)

    for idx, i in enumerate(res.transform.args):
        if not (v := explain(i, False)):
            continue
        res.transform.args[idx] = v.transform
        res.children.insert(idx, v)
    if len(res.children) > n and not n:
        res.children.append(Step(res.label, op))
    if not res.changed and not res.children:
        return expr if default else None
    return res


_steps: dict[int, Step] = {}
_verbose: bool = False
_curr_hist: list = None


__all__ = [
    "ETNode",
    "ETBranch",
    "ETOperator",
    "Step",
    "verbose",
    "set_verbosity",
    "tracked",
    "explain",
    "register",
    "scoped",
]
