from contextlib import contextmanager
from copy import copy
from dataclasses import dataclass, field
from itertools import chain, zip_longest
from functools import lru_cache, wraps
from enum import Enum
from typing import Any, Iterator


from rich.text import Text
from rich.console import Group
from rich.panel import Panel
from rich.console import Group, Console
from rich.padding import Padding

from .constants import SYMBOLS
from .print_ import superscript, strip_ansi, colorize_ansi


class ETNode:
    is_align = False

    def __init__(self, result):
        self.result = result
        self.is_align = self.result.__class__.__name__ == "Comparison"
        # self.is_align=True

    def header(self) -> str:
        return str(self.result)

    def __repr__(self):
        return ""  # str(self.result)

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

    def tostr(self, args, _):
        a, b = args
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


class OPBinaryType(Enum):
    EQ = 0
    GT = 1
    GE = 2
    LT = 3
    LE = 4

    def tostr(self, args, _):
        left, right = args
        return SYMBOLS.get(self.name).join("  ").join((str(left), str(right)))


class OPSpecials(Enum):
    VERIFY = 0

    def tostr(self, args, result) -> str:
        if self is OPSpecials.VERIFY:
            return str(args[0]) + " " + "❌✅📉"[result]


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
        else:
            self.type = id
        self.args = list(args)
        self.result = result

    def __repr__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(self.args, self.result)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + str(tuple(self.args))

    def header(self) -> str:
        if isinstance(self.type, OPSpecials):
            return str(self)
        return str(self) + " --> " + str(self.result)


class ETBranch(ETNode):
    def __init__(self, result):
        super().__init__(list(result))
        if self.result[0].__class__.__name__ == "Comparison":
            self.result.sort(key=str)

    def __repr__(self):
        if self.result[0].__class__.__name__ != "System":
            return ",  ".join(map(str, self.result))
        data = [str(i).split("\n") for i in self.result]
        return "\n".join(
            "    ".join(items) for items in zip_longest(*data, fillvalue="")
        )

    def totex(self):
        return ",\\quad ".join(i.totex() for i in self.result)


@dataclass
class Step:
    label: str
    transform: ETOperator | ETNode
    children: list = field(default_factory=list)

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
            idx = ""  # str(index) + ". " if index else ""
            lpad = depth + 1
            label = step.label + ": " if step.label else ""
            if not step.children:
                res = Text.from_ansi(f"{idx}{label}{step.transform.header()}")
                res.pad_left(lpad)
                res.truncate(width, overflow="ellipsis")
                return res
            p = len(step.children) > 1
            lpad *= not len(step.children)
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
                Text(f"Final: {step.transform.result}"),
            )
            res.renderables[0].truncate(width, overflow="ellipsis")
            res.renderables[0].pad_left(lpad)
            res.renderables[-1].truncate(width, overflow="ellipsis")
            res.renderables[-1].pad_left(lpad + 2)
            if depth == 0 or step.children:
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
def scoped(scope: list):
    global _curr_hist
    before = _curr_hist
    _curr_hist = scope
    try:
        yield
    finally:
        _curr_hist = before


def tracked(identifier: str, label: str = "", default_show: bool = True):

    def tracked_func(func):
        @wraps(func)
        @lru_cache
        def wrapper(*args, **kwargs):
            history = []
            with scoped(history):
                result = func(*args, **kwargs)

            if not _verbose or (
                not wrapper._is_simplified(result, args) and not any(history)
            ):
                return result
            result = copy(result)
            step = Step(label, ETOperator(identifier, args, result), history)
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

        wrapper._is_simplified = lambda *_: default_show
        wrapper.check_changed = check_changed
        wrapper.register = register
        return wrapper

    return tracked_func


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
