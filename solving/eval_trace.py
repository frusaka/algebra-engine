from __future__ import annotations
from itertools import zip_longest
import re
from enum import Enum
from typing import Any
from contextlib import contextmanager

from utils import superscript
from utils.print_ import truncate


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
        from rich.text import Text
        from rich.console import Group

        res = [Text.from_ansi(i) for i in str(self).split("\n")]
        [t.truncate(80 - 4 * depth, overflow="ellipsis") for t in res]
        if len(res) == 1:
            return res[0]
        return Group(*res)


class ETBranchNode(ETNode):
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


class ETOperatorType(Enum):
    ADD = "#21ba3a"
    SUB = "#d7170b"
    DIV = "#ffc02b"
    TIMES = "#0d80f2"
    POW = "#a219e6"
    SQRT = 6

    def tostr(self, value):
        if value.__class__.__name__ == "Add":
            value = str(value).join("()")
        else:
            value = str(value)
        color = None
        if self.name == "ADD":
            res = "+" + value
        elif self.name == "SUB":
            res = "-" + value
        elif self.name == "TIMES":
            res = "×" + value
        elif self.name == "DIV":
            res = "÷" + value
        elif self.name == "POW":
            res = "( )" + superscript(value)
        elif self.name == "SQRT":
            res = "√( )"
            if value != "2":
                res = superscript(value) + res
            color = ETOperatorType.POW.value
        return colorize_ansi(res, color or self.value)

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
            return "\\textcolor{#a219e6}" + ("(\\phantom{a})^" + str(value)).join("{}")
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
        self.is_align = True

    def __repr__(self):
        return truncate(" " * self.padding) + "⇓" + self.type.tostr(self.value)

    def totex(self):
        return "\\Downarrow" + self.type.totex(self.value)


class ETTextNode(ETNode):
    def __init__(self, result: str, color=None):
        super().__init__(result)
        self.color = color

    def __repr__(self):
        if self.color:
            return colorize_ansi(self.result, self.color)
        return self.result

    def totex(self) -> str:
        res = "\\text{$}".replace("$", self.result)
        if self.color:
            return "\\textcolor{$}".replace("$", self.color) + res.join("{}")
        return res


class ETSubNode(ETNode):
    def __init__(self, old: str, new: Any):
        self.old = old
        self.new = new
        self.is_align = False

    def __repr__(self):
        return "Substitute {0} with {1}".format(
            colorize_ansi(self.old, "#d7170b"),
            colorize_ansi(str(self.new), "#21ba3a"),
        )

    def totex(self):
        old = "\\textcolor{#d7170b}" + self.old.join("{}")
        new = "\\textcolor{#21ba3a}" + self.new.totex().join("{}")
        return "\\text{Substitute }" + old + "\\text{ with }" + new


class ETVerifyNode(ETNode):
    def __init__(self, result, state: bool):
        super().__init__(result)
        self.state = state

    def __repr__(self):
        return truncate(str(self.result), 78) + " " + "❌✅📉"[self.state]

    def totex(self):
        return self.result.totex() + "❌✅📉"[self.state]


class ETQuadraticNode(ETNode):
    def __init__(self, var, a, b, c):
        self.var = var
        self.a = a
        self.b = b
        self.c = c
        self.is_align = True

    def __repr__(self):
        a = colorize_ansi(self.a, "#3f51b5")
        b = colorize_ansi(self.b, "#e91e63")
        c = colorize_ansi(self.c, "#4caf50")

        return f"{self.var} = (-{b} ± √({b}²-4·{a}·{c}))/2·{a}"

    def totex(self):
        a, b, c = self.a, self.b, self.c
        a = "\\textcolor{#3f51b5}" + self.a.totex().join("{}")
        b = "\\textcolor{#e91e63}" + self.b.totex().join("{}")
        c = "\\textcolor{#4caf50}" + self.c.totex().join("{}")

        return (
            f"{self.var}="
            + "\\frac"
            + ("-{b} \\pm" + "\\sqrt" + f"{b}^2-4\\cdot{a}\\cdot{c}".join("{}")).join(
                "{}"
            )
            + f"2\\cdot{a}".join("{}")
        )


class ETSteps:
    data = []
    history = [data]
    idx = [0]

    @classmethod
    def __bool__(cls):
        return bool(cls.data)

    @classmethod
    def clear(cls):
        cls.data.clear()
        cls.history = [cls.data]
        cls.idx = [0]

    @classmethod
    def register(cls, step):
        cls.history[-1].append(step)

    @classmethod
    def create_branches(cls, amount: int):
        # Perhaps parameters should be the tittles?
        branches = [[] for _ in range(amount)]
        cls.history[-1].extend(branches)
        cls.history.append(branches)
        cls.idx.append(0)

    @classmethod
    def next_branch(cls):
        if cls.idx[-1]:
            cls.history.pop()
        branch_list = cls.history[-1]
        cls.history.append(branch_list[cls.idx[-1]])
        cls.idx[-1] += 1

    @classmethod
    def end_branches(cls):
        cls.history.pop()
        cls.history.pop()
        cls.idx.pop()

    class _BranchIterator:
        def __init__(self, num: int):
            self.num = num
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.count >= self.num:
                raise StopIteration
            ETSteps.next_branch()
            self.count += 1
            return self.count - 1

    @classmethod
    @contextmanager
    def branching(cls, amount: int):
        cls.create_branches(amount)
        try:
            yield cls._BranchIterator(amount)
        finally:
            cls.end_branches()

    @classmethod
    def tostr(cls):
        if not cls.data:
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
            top = "╭" + "─" * lpad + tittle + "─" * rpad + "╮"
            body = ["│" + pad_line(line, max_len) + "│" for line in lines[1:]]
            bottom = "╰" + "─" * width + "╯"
            return [top] + body + [bottom]

        def process(item):
            if isinstance(item, ETNode):
                return str(item).split("\n")
            return box([j for i in item for j in process(i)])

        return "\n".join(process(cls.data))

    @classmethod
    def torich(cls):
        from rich.panel import Panel
        from rich.console import Group

        def to_rich(item, depth):
            if isinstance(item, ETNode):
                return item.torich(depth)
            if len(item) < 2:
                return ""
            items = Group(*(j for i in item[1:] if (j := to_rich(i, depth + 1))))
            return Panel(items, title=item[0].torich(max(0, depth)), expand=False)

        return to_rich(cls.data, -1)

    @classmethod
    def toHTML(cls) -> str:
        def tex(data, depth):
            if not data:
                return ""
            if isinstance(data, ETNode):
                return data.totex().join(("$$", "$$"))
            content = "".join(tex(i, depth + idx) for idx, i in enumerate(data[1:], 1))
            return f"""
            <div class="accordion" data-ae-title="{data[0]}">
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button
                            class="accordion-button"
                            type="button"
                            data-bs-toggle="collapse"
                            data-bs-target="#ae-br{depth}-body"
                            aria-expanded="true"
                            aria-controls="ae-br{depth}-body">
                            {data[0]}
                        </button>
                    </h2>
                    <div id="ae-br{depth}-body"
                        class="accordion-collapse collapse show"
                        >
                        <div class="accordion-body">{content}</div>
                    </div>
                </div>
            </div>
            """

        return tex(cls.data, 1)


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
