from contextlib import contextmanager
from copy import copy as copy_
import re
from functools import lru_cache, wraps
from enum import Enum
from typing import Any, Iterator


from rich.text import Text
from rich.console import Group
from rich.panel import Panel
from rich.console import Group, Console
from rich.padding import Padding

from utils import superscript, SYMBOLS


def strip_ansi(text):
    res = ANSI_ESCAPE_RE.sub("", text)
    return res


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def colorize_ansi(text: str, hex_color: str) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


class ETNode:
    is_align = False

    def __init__(self, result):
        self.result = result
        self.is_align = self.result.__class__.__name__ == "Comparison"
        # self.is_align=True

    def __repr__(self):
        return str(self.result)

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
        a = str(a).join("()") if a.__class__ is not ETNode else str(a)
        b = str(b).join("()") if b.__class__ is not ETNode else str(b)
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


class OPSpecials(Enum):
    VERIFY = 0

    def tostr(self, *args) -> str:
        return str(args[0])
        if self is OPSpecials.VERIFY:
            return str(args[0]) + " " + "❌✅📉"[args[1]]


class ETOperator(ETNode):
    def __init__(self, id: str, args: tuple[ETNode]) -> None:
        if t := OPArithmeticType.__members__.get(id, None):
            self.type = t
        elif t := OPSpecials.__members__.get(id, None):
            self.type = t
        else:
            self.type = id

        self.args = list(args)

    def __repr__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(*self.args)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + str(tuple(self.args))


class Step:
    def __init__(
        self,
        label: str,
        operator: ETOperator,
        result: Any,
        children: list = None,
    ):
        self.label = label or ""
        self.operator = operator
        self.result = result
        self.children = children or []
        self._finished = False

    def __repr__(self) -> str:
        def _str(step, depth):
            if not step.children:
                return f"{step.label}: {step.operator} --> {step.result}"
            res = f"{step.label}: {step.operator}"
            for idx, i in enumerate(step.children, 1):
                res += "\n" + "   " * depth + str(idx) + ". " + _str(i, depth + 1)
            res += "\n" + "   " * depth + str(idx + 1) + f". Final: {step.result}"
            return res

        return _str(self, 1)

    def __rich_console__(self, console: Console, *_) -> Iterator[Text | Panel | Group]:
        def rich(step, depth, index):
            width = console.width - 3 - depth * 4
            idx = ""  # str(index) + ". " if index else ""
            lpad = depth + 1
            label = step.label + ": " if step.label else ""
            if not step.children:
                res = Text.from_ansi(f"{idx}{label}{step.operator} --> {step.result}")
                res.pad_left(lpad)
                res.truncate(width, overflow="ellipsis")
                return res
            p = len(step.children) > 1
            lpad *= not p
            res = Group(
                Text.from_ansi(f"{idx}{label}{step.operator}"),
                Padding(
                    Group(
                        *(
                            rich(i, 1, idx if p else 0)
                            for idx, i in enumerate(step.children, 1)
                        )
                    ),
                    (0, 0, 0, lpad),
                ),
                Text(f"Final: {step.result}"),
            )
            res.renderables[0].truncate(width, overflow="ellipsis")
            res.renderables[0].pad_left(lpad)
            res.renderables[-1].truncate(width, overflow="ellipsis")
            res.renderables[-1].pad_left(lpad + 2)
            if depth == 0 or p:
                return Panel(res, expand=False)
            return res

        return iter((rich(self, 0, 0),))


def set_verbosity(value: bool) -> None:
    global _verbose
    _verbose = value


def verbose() -> bool:
    return _verbose


def register(step: Step | Any) -> None:
    if not _verbose or _curr_hist is None:
        return
    if step is not None and type(step) is not Step:
        step = _steps.get(id(step), None)
    if step is None:
        return
    _curr_hist.append(step)


@contextmanager
def _scoped(scope: list):
    global _curr_hist
    before = _curr_hist
    _curr_hist = scope
    try:
        yield
    finally:
        _curr_hist = before


def tracked(identifier: str, label: str = ""):

    def tracked_func(func):
        @wraps(func)
        @lru_cache
        def wrapper(*args, **kwargs):
            history = []
            with _scoped(history):
                result = func(*args, **kwargs)

            changed = wrapper._is_simplified(result, args)
            if not _verbose or (not changed and not any(history)):
                return result
            result = copy(result)  # , id(result))
            if any(history) and changed:
                history.append(Step(label, ETOperator(identifier, args), result))
            step = Step(label, ETOperator(identifier, args), result, history)
            # A recursive Function
            if res := _steps.get(id(result), None):
                print("Recursion?:", step.operator, "vs.", res.operator)
            else:
                # result = copy_(result)
                # print("storing", result)
                _steps[id(result)] = step
            return result

        def check_changed(fn):
            wrapper._is_simplified = fn
            return fn

        def register(expr):
            if not _verbose or _curr_hist is None:
                return
            step = _steps.get(id(expr))
            if step is None:
                return
            wrapper.steps.append(step)

        wrapper._is_simplified = lambda *_: True
        wrapper.check_changed = check_changed
        wrapper.register = register
        return wrapper

    return tracked_func


def explain(expr, default=True) -> Step | Any:
    if not (res := _steps.get(id(expr), None)):
        if expr.__class__.__name__ == "System":
            print("Juice", expr)
            res = Step("", ETNode(expr), [r for n in expr if (r := explain(n, False))])
            _steps[id(expr)] = res
            return res
        print(expr)
        return expr if default else None
    op = copy_(res.operator)
    op.args = op.args.copy()
    n = len(res.children)

    for idx, i in enumerate(res.operator.args):
        if not (v := explain(i, False)):
            continue
        res.operator.args[idx] = v.operator
        res.children.insert(idx, v)
    if len(res.children) > n:
        res.children.append(Step(res.label, op, res.result))

    return res


@lru_cache(maxsize=1000)
def copy(value):
    return copy_(value)


copy = lru_cache(maxsize=10000)(copy)

_steps: dict[int, Step] = {}
_verbose: bool = False
_curr_hist: list = None

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


__all__ = [
    "ETNode",
    "ETOperator",
    "Step",
    "verbose",
    "set_verbosity",
    "tracked",
    "explain",
    "register",
]
