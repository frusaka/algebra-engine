from __future__ import annotations
import re
from enum import Enum
from typing import Any
from contextlib import contextmanager

from utils import superscript


class ETNode:
    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return repr(self.result)

    def totex(self, align=True):
        return self.result.totex(align)


class ETBranchNode(ETNode):
    def __init__(self, result):
        super().__init__(list(result))
        if self.result[0].__class__.__name__ is "Comparison":
            self.result.sort(key=str)

    def __repr__(self):
        if self.result[0].__class__.__name__ is not "System":
            return ",  ".join(map(repr, self.result))
        data = [repr(i).split("\n") for i in self.result]
        return "\n".join("    ".join(items) for items in zip(*data))

    def totex(self, align):
        return "&" * align + ",\\quad ".join(i.totex(0) for i in self.result)


class ETOperatorType(Enum):
    ADD = 0
    SUB = 1
    DIV = 2
    TIMES = 4
    POW = 5
    SQRT = 6

    def tostr(self, value):
        if self.name == "ADD":
            return colorize_ansi("+" + repr(value), "#21ba3a")
        if self.name == "SUB":
            return colorize_ansi("-" + repr(value), "#d7170b")
        if self.name == "TIMES":
            return colorize_ansi("×" + repr(value), "#0d80f2")
        if self.name == "DIV":
            return colorize_ansi("÷" + repr(value), "#ffc02b")
        if self.name == "POW":
            return colorize_ansi("( )" + superscript(value), "#a219e6")
        if self.name == "SQRT":
            res = "√( )"
            if value != 2:
                res = superscript(value) + res
            return colorize_ansi(res, "#a219e6")

    def totex(self, value):
        if self.name == "ADD":
            return "\\textcolor{#21ba3a}" + ("+" + value.totex()).join("{}")
        if self.name == "SUB":
            return "\\textcolor{#d7170b}" + ("-" + value.totex()).join("{}")
        if self.name == "TIMES":
            return "\\textcolor{#0d80f2}" + ("\\times" + value.totex().join("{}")).join(
                "{}"
            )
        if self.name == "DIV":
            return "\\textcolor{#ffc02b}" + ("\\div" + value.totex().join("{}")).join(
                "{}"
            )
        if self.name == "POW":
            return "\\textcolor{#a219e6}" + (
                "(\\phantom{a})^" + value.totex().join("{}")
            ).join("{}")
        if self.name == "SQRT":
            if value == 2:
                return "\\textcolor{#a219e6}" + "{\\sqrt{\\phantom{a}}}"
            return "\\textcolor{#a219e6}" + (
                f"\\sqrt[{value}]" + "{\\phantom{a}}"
            ).join("{}")


class ETOperatorNode(ETNode):
    def __init__(self, type: ETOperatorType, value: Any, padding: int):
        self.type = type
        self.value = value
        self.padding = padding

    def __repr__(self):
        return " " * self.padding + "⇓" + self.type.tostr(self.value)

    def totex(self, align=True):
        return "&\\Downarrow".replace("&", "&" * align) + self.type.totex(self.value)


class ETTextNode(ETNode):
    def __init__(self, result: str, color=None):
        super().__init__(result)
        self.color = color

    def __repr__(self):
        if self.color:
            return colorize_ansi(self.result, self.color)
        return self.result

    def totex(self, align=True) -> str:
        align = "&" * align
        res = "\\text{$}".replace("$", self.result)
        if self.color:
            return "&\\textcolor{$}".replace("$", self.color).replace(
                "&", align
            ) + res.join("{}")
        return align + res


class ETSubNode(ETNode):
    def __init__(self, old: str, new: Any):
        self.old = old
        self.new = new

    def __repr__(self):
        return "Substitute {0} with {1}".format(
            colorize_ansi(self.old, "#d7170b"),
            colorize_ansi(repr(self.new), "#21ba3a"),
        )

    def totex(self, align=True):
        old = "\\textcolor{#d7170b}" + self.old.join("{}")
        new = "\\textcolor{#21ba3a}" + self.new.totex(0).join("{}")
        return (
            "&\\text{Substitute }".replace("&", "&" * align)
            + old
            + "\\text{ with }"
            + new
        )


class ETVerifyNode(ETNode):
    def __init__(self, result, state: bool):
        super().__init__(result)
        self.state = state

    def __repr__(self):
        return repr(self.result) + "❌✅📉"[self.state]

    def totex(self, align):
        return "&" * align + self.result.totex(0) + "❌✅📉"[self.state]


class ETQuadraticNode(ETNode):
    def __init__(self, var, a, b, c):
        self.var = var
        self.a = a
        self.b = b
        self.c = c

    def __repr__(self):
        a = colorize_ansi(self.a, "#3f51b5")
        b = colorize_ansi(self.b, "#e91e63")
        c = colorize_ansi(self.c, "#4caf50")

        return f"{self.var} = (-{b} ± √({b}²-4·{a}·{c}))/2·{a}"

    def totex(self, align=True):
        a, b, c = self.a, self.b, self.c
        a = "\\textcolor{#3f51b5}" + self.a.totex().join("{}")
        b = "\\textcolor{#e91e63}" + self.b.totex().join("{}")
        c = "\\textcolor{#4caf50}" + self.c.totex().join("{}")

        return (
            f"{self.var}&="
            + "\\frac"
            + ("-{b} \\pm" + "\\sqrt" + f"{b}^2-4\\cdot{a}\\cdot{c}".join("{}")).join(
                "{}"
            )
            + f"2\\cdot{a}".join("{}")
        )


class ETSteps:
    def __init__(self, data=None):
        self.data = data if data is not None else []
        self.history = [self.data]
        self.idx = [0]

    def __bool__(self):
        return bool(self.data)

    def clear(self):
        self.data.clear()
        self.history = [self.data]
        self.idx = [0]

    def register(self, step):
        self.history[-1].append(step)

    def create_branches(self, amount: int):
        # Perhaps parameters should be the tittles?
        branches = [[] for _ in range(amount)]
        self.history[-1].extend(branches)
        self.history.append(branches)
        self.idx.append(0)

    def next_branch(self):
        if self.idx[-1]:
            self.history.pop()
        branch_list = self.history[-1]
        self.history.append(branch_list[self.idx[-1]])
        self.idx[-1] += 1

    def end_branches(self):
        self.history.pop()
        self.history.pop()
        self.idx.pop()

    class _BranchIterator:
        def __init__(self, steps: ETSteps, num: int):
            self.steps = steps
            self.num = num
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.count >= self.num:
                raise StopIteration
            self.steps.next_branch()
            self.count += 1
            return self.count - 1

    @contextmanager
    def branching(self, amount: int):
        self.create_branches(amount)
        try:
            yield self._BranchIterator(self, amount)
        finally:
            self.end_branches()

    def __repr__(self):
        if not self.data:
            return ""
        padding = 1

        def pad_line(line, max_len):
            visible = strip_ansi(line)
            pad = " " * padding
            trailing = " " * (max_len - len(visible) - (visible[-1] in "❌✅📉"))
            return pad + line + trailing + pad

        def box(lines):
            if not lines:
                return lines
            max_len = max(
                len(strip_ansi(line)) + (line[-1] in "❌✅📉") for line in lines
            )
            width = max_len + 2 * padding
            tittle = " " * padding + lines[0] + " " * padding
            spacing = width - len(tittle)
            lpad, rpad = (spacing // 2,) * 2
            if spacing % 2:
                lpad += 1
            top = "┌" + "─" * lpad + tittle + "─" * rpad + "┐"
            body = ["│" + pad_line(line, max_len) + "│" for line in lines[1:]]
            bottom = "└" + "─" * width + "┘"
            return [top] + body + [bottom]

        def process(item):
            if isinstance(item, ETNode):
                return repr(item).split("\n")
            nested_lines = []
            for sub in item:
                nested = process(sub)
                nested_lines.extend(nested)
            return box(nested_lines)

        return "\n".join(process(self.data))

    def totex(self, align=True, _depth=0) -> str:
        if not self.data:
            return ""
        res = "\\\\".join(
            (
                step.totex(1)
                if isinstance(step, ETNode)
                else ETSteps(step).totex(_depth=1)
            )
            for step in self.data
        )
        res = res.join(("\\begin{aligned}", "\\end{aligned}"))
        return res.join(("&\\boxed{".replace("&", "&" * _depth), "}"))


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text):
    res = ANSI_ESCAPE_RE.sub("", text)
    return res


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def colorize_ansi(text: str, hex_color: str) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


steps = ETSteps()
