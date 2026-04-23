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


def ref(value, force_keep=False):
    if force_keep:
        return lambda: value
    try:
        return weakref.ref(value)
    except TypeError:
        print("Na", value)
        return lambda: value


class ETNode:
    def __init__(self, result):
        result = copy(result)
        self.args = (result,)
        self.result = result
        self.changed = True

    def __repr__(self):
        return str(self.result)

    def header(self) -> str:
        return str(self)

    def tex_header(self) -> str:
        return tex(self.result)

    def totex(self):
        return self.tex_header()

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

    def totex(self, a, b):
        color = self.value if self.name != "SQRT" else OPArithmeticType.POW.value
        color = "\\textcolor{" + color + "}"
        a = (
            tex(a).join(("\\left(", "\\right)"))
            if a.__class__.__name__ in {"ETOperator", "Add"}
            else str(a)
        )
        b = (
            tex(b).join(("\\left(", "\\right)"))
            if b.__class__.__name__ in {"ETOperator", "Add"}
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
        return self.name.lower().join((tex(left), tex(right)))


class OPSpecials(Enum):
    VERIFY = 0
    SUBS = 1
    SOLVE = 2

    def tostr(self, *args) -> str:
        if self is OPSpecials.VERIFY:
            if len(args) == 1:
                return str(args[0])
            return "verify" + str(args)
        if self is OPSpecials.SOLVE:
            return "Solve for " + str(args[1])
        return "Substitue {0} with {1}".format(
            colorize_ansi(str(args[0]), OPArithmeticType.SUB.value),
            colorize_ansi(str(args[1]), OPArithmeticType.ADD.value),
        )

    def totex(self, *args) -> str:
        if self is OPSpecials.VERIFY:
            if len(args) == 1:
                return args[0].totex()
            return "verify" + ",".join(map(tex, args)).join("()")
        return "Substitue {0} with {1}".format(args[0].totex(), args[1].totex())


class ETOperator(ETNode):
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
        args: tuple[ETNode],
        result: Any,
        changed: bool = True,
        force_keep: bool = False,
    ) -> None:
        if t := self._options.get(id, None):
            self.type = t
            if self.type is OPSpecials.VERIFY:
                result = "❌✅📉"[result]
        else:
            self.type = id
        self.args = list(args)  # copy(i) for i in args)
        self._result = ref(result, False)  # (_keep or force_keep) and changed)
        self.changed = changed

    @property
    def result(self):
        return self._result()

    def __repr__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(*self.args)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + str(tuple(self.args))

    def header(self):
        return str(self) + " ⟶ " + str(self.result)

    def totex(self) -> str:
        if type(self.type) is not str:
            return self.type.totex(*self.args)
        if len(self.args) == 1:
            return "\\mathrm{" + self.type + "}" + tex(self.args[0]).join("()")
        return "\\mathrm{" + self.type + "}" + ",".join(map(tex, self.args)).join("()")

    def tex_header(self) -> str:
        return self.totex() + "\\longrightarrow " + tex(self.result)


class ETBranch(ETNode):
    def __init__(self, result):
        args = list(copy(i) for i in result)
        if args[0].__class__.__name__ == "Comparison":
            args.sort(key=str)
        self.args = args
        self.changed = True

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

    def tex_header(self) -> str:
        return ",\\quad ".join(map(tex, self.args))


@dataclass
class Step:
    label: str
    transform: ETOperator | ETNode
    children: list[Step] = field(default_factory=list)

    def __post_init__(self):
        if type(self.transform) is not ETOperator:
            print("passing", self.transform)
            return

        def delete_unused(idx):
            if idx in _steps:
                step = _steps.pop(idx)
                for i in step.children:
                    delete_unused(id(i.transform.result))

        try:
            weakref.finalize(
                self.transform.result, delete_unused, id(self.transform.result)
            )
        except TypeError:
            pass

    def __str__(self) -> str:
        def _str(step, depth):
            label = step.label + ": " if step.label else ""
            if not step.children:
                return f"{label}{step.transform.header()}"
            res = (
                f"{label}{step.transform}"
                if type(self.transform) is ETOperator
                else label
            )
            for idx, i in enumerate(step.children, 1):
                res += "\n" + "   " * depth + str(idx) + ". " + _str(i, depth + 1)
            res += "\n" + "   " * depth + f"Result: {step.transform.result}"
            return res

        return _str(self, 1)

    def __rich_console__(self, console: Console, *_) -> Iterator[Text | Panel]:
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
            title = idx + label
            if type(step.transform) is ETOperator:
                title += str(step.transform)
            res = Group(
                Text.from_ansi(title),
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
                    if type(step.transform) is not ETNode
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

    def toJSON(self):
        def json(step: Step):
            label = step.label + ": " if step.label else ""
            delims = ("$$", "$$") if not label else ("\\(", "\\)")
            if not step.children:
                return label + step.transform.tex_header().join(delims)
            res = [
                label
                + (
                    step.transform.totex().join(delims)
                    if type(step.transform) is ETOperator
                    else ""
                ),
                *(json(i) for i in step.children),
                (
                    f"Result: \\({tex(step.transform.result)}\\)"
                    if type(step.transform) is ETOperator
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


def register(step: Step | Any, scoped=True, reason=None) -> None:
    if not _verbose or scoped and _curr_hist is None:
        return
    if step is not None and type(step) is not Step:
        step = _steps.get(id(step), None)
        if step:
            if reason is not None:
                step.label = reason
            # if forced:
            #     step.changed = True
            if not step.transform.changed and not step.children:
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


@contextmanager
def force_keep():
    global _keep
    before = _keep
    _keep = True
    try:
        yield
    finally:
        _keep = before


P = ParamSpec("P")
R = TypeVar("R")


class Tracked(Generic[P, R]):
    depth = 0

    def __init__(
        self,
        func: Callable[P, R],
        id: str = None,
        label: str = None,
        force_keep: bool = False,
    ):
        id = id if id is not None else func.__name__
        label = label if label is not None else ""
        self.func = func  # lru_cache(maxsize=500)(func)
        self.id = id
        self.label = label
        self.force_keep = force_keep
        update_wrapper(self, func)
        self.__signature__ = inspect.signature(func)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        history = []
        Tracked.depth += 1
        with scoped(history):
            # if self.force_keep:
            #     with force_keep():
            #         result = self.func(*args, **kwargs)
            # else:
            result = self.func(*args, **kwargs)

        Tracked.depth -= 1
        if not _verbose:  # or not (changed := self._is_simplified(result, args)):
            return result
        if len(args) == 1 and result == args[0]:
            return args[0]
        result = copy(result)
        _steps[id(result)] = Step(
            self.label,
            ETOperator(
                self.id,
                args,
                result,
                self._is_simplified(result, args),
            ),
            history,
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


def tracked(id: str = None, label: str = None, force_keep: bool = False):
    def wrapper(func: Callable[P, R]) -> Tracked[P, R]:
        return Tracked(func, id, label, force_keep)

    return wrapper


def explain(expr, default=True) -> Step | Any:
    if not (res := _steps.get(id(expr), None)):
        return expr if default else None
    op = copy(res.transform)
    op.args = op.args.copy()
    n_args = op.args.copy()
    n = len(res.children)

    for idx, i in enumerate(res.transform.args):
        if not (v := explain(i, False)):
            continue
        n_args[idx] = v.transform
        res.children.insert(idx, v)
        _steps.pop(id(v.transform.result))
    res.transform.args = n_args
    if len(res.children) > n and not n:
        res.children.append(Step(res.label, op))
    if not res.transform.changed and not res.children:
        return expr if default else None
    return res


_steps: dict[int, Step] = {}
_verbose: bool = False
_curr_hist: list = None
_keep: bool = False


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
    "force_keep",
]
