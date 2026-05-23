from __future__ import annotations

from typing import Any, Iterator

from copy import copy
from dataclasses import dataclass
from itertools import chain
from enum import Enum
import weakref

from rich.text import Text
from rich.console import Group
from rich.panel import Panel
from rich.console import Group, Console
from rich.padding import Padding


from ..constants import SYMBOLS
from ..print_ import superscript, colorize_ansi, print_system


def tex(value):
    return getattr(value, "totex", lambda: str(value))()


_del_seen = set()


def delete_unused(idx):
    if type(idx) is int:
        if idx not in _steps:
            return
        step = _steps.pop(idx)
    else:
        step = idx
        if (idx := id(step.result)) in _steps:
            _steps.pop(idx)
    if id(step) in _del_seen:
        return
    _del_seen.add(id(step))
    # print("deleting", step)
    for i in step.children:
        delete_unused(i)
        # delete_unused(i)
    _del_seen.remove(id(step))
    if id(step) in _exp_seen:
        _exp_seen.remove(id(step))
    # step = _steps.pop(id(step.result))


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
    NE = 5

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
    SYS = 5

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
        if self is OPSpecials.SYS:
            return print_system(args)

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
        else:
            self.type = id
        if not hasattr(args, "__iter__"):
            args = (args,)
        self.args = list(args)
        self._result = ref(result, force_keep, self)
        self.children = children or []
        self.reason = reason
        self.changed = changed
        self._args = tuple(self.args)
        self._collapsed = False

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
        if not self.changed and not self.children:
            return
        res = self.result
        self._result = lambda: res

    def __str__(self) -> str:
        if type(self.type) is not str:
            return self.type.tostr(*self.args)
        # if self.type == "subs":
        #     return str(self.result)
        if len(self.args) == 1:
            return self.type + str(self.args[0]).join("()")
        return self.type + ", ".join(map(str, self.args)).join("()")

    def header(self):
        if self.type is OPSpecials.STATE:
            return str(self)
        return str(self) + " --> " + str(self.result)

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

    def __rich__(self) -> Text | Panel:
        PANEL_COLORS = ["#F0E68C", "#9370DB", "#87CEFA"]

        def rich(step: Step, depth, index):
            idx = str(index) + ". " if index else ""
            lpad = bool(depth) + 1
            label = step.reason + ": " if step.reason else ""
            if not step.children and not isinstance(step.result, Exception):
                return Text.from_ansi(f"{idx}{label}{step.header()}").markup
            p = len(step.children) > 1
            lpad *= not len(step.children) or not bool(index) or not depth
            org_title = title = "[bold]" + idx + label + "[/bold]"
            if step.result is not None:
                title += Text.from_ansi(str(step)).markup
            true_final = final = ""
            border = PANEL_COLORS[depth % len(PANEL_COLORS)]
            if isinstance(step.result, bool):
                border = ["red", "green"][step.result]
            if step.result is not None:
                if isinstance(step.result, Exception):
                    true_final = f"[bold red]{type(step.result).__name__}:[/bold red] {step.result}"
                    if not step.children:
                        final = true_final
                    border = "red"
                elif step.result is not step.children[-1].result:
                    final = f"[bold]Result:[/bold] {step.result}"
            title, final = (
                Text.from_markup(title).markup,
                Text.from_markup(final).markup,
            )
            res = Group(
                title,
                Padding(
                    Group(
                        *(
                            rich(i, depth + 1, idx if p else 0)
                            for idx, i in enumerate(step.children, 1)
                        )
                    ),
                    (0, 0, 0, lpad),
                ),
                final,
            )
            res.step_header = (
                (org_title + Text.from_ansi(step.header()).markup)
                if not isinstance(step.result, Exception)
                else " --> ".join((title, true_final))
            )
            res.collapsed = step._collapsed
            if not step.children:
                return res.step_header
            if not final:
                res.renderables.pop()
            # return res
            if depth == 0 or step.children and index and step.result is not None:
                return Panel(res, border_style=border, expand=False, highlight=True)
            return res

        return rich(self, 0, 0)

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


def is_eq_priority(a, b) -> bool:
    return a == b or {a, b} in (
        {OPArithmeticType.ADD, OPArithmeticType.SUB},
        {OPArithmeticType.MUL, OPArithmeticType.DIV},
    )


_exp_seen = set()


def _explain(expr) -> Step | Any:
    if not (res := _steps.get(id(expr), None)):
        return
    if id(res) in _exp_seen:
        if not res.changed and not res.children:
            return
        return res
    op = copy(res)
    res.children = []
    for idx, i in enumerate(res.args):
        if type(i) is Step or not (v := _explain(i)):
            continue
        res.args[idx] = v
        if is_eq_priority(v.type, res.type) and v.children:
            res.children.extend(v.children)
        else:
            res.children.append(v)
        _steps.pop(id(v.result))

    res.children.extend(op.children)
    if len(res.children) > len(op.children) and op.changed:
        op.children = []
        res.children.append(op)
    if not res.changed and not res.children:
        return
    return res


def explain(
    expr, default=True, maxdepth: int | None = 2, adaptive=True
) -> Step | None | Any:
    if not (res := _explain(expr)):
        return expr if default else None
    if maxdepth is None:
        return res

    from datatypes.expr import Expr
    from solving.core import Comparison, Interval, IntervalUnion, System

    # To be revised
    def priority(val):
        if isinstance(val, Expr):
            return 1
        if isinstance(val, (System, Comparison, Interval, IntervalUnion)):
            return 2
        # if isinstance(val, System):
        #     return 3
        if hasattr(val, "__iter__"):
            return 1 + next(iter(val))
        return 5

    def dfs(step: Step, depth):
        if not step.children:
            return step
        if depth == 0 and (
            not adaptive or priority(step.children[0]._args[0]) < priority(res._args[0])
        ):
            step._collapsed = True
            return step
        [dfs(i, max(0, depth - 1)) for i in step.children]
        return step

    return dfs(res, maxdepth)


_steps: dict[int, Step] = {}
_verbose: bool = False

__all__ = ["Step", "verbose", "set_verbosity", "explain"]
