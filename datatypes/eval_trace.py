from __future__ import annotations
from enum import Enum
from typing import Any, Generator
from contextlib import contextmanager


class ETNode:
    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return str(self.result)

    def totex(self, align=True):
        return self.result.totex(align)


class ETBranchNode(ETNode):
    def __init__(self, result):
        super().__init__(list(result))

    def __repr__(self):
        return ",    ".join(str(i) for i in self.result)

    def totex(self, align):
        return "&" * align + ",\\quad ".join(i.totex(0) for i in self.result)


class ETOperatorType(Enum):
    ADD = 0
    SUB = 1
    DIV = 2
    TIMES = 4
    POW = 5
    SQRT = 6

    def torich(self, value):
        if self.name == "ADD":
            return "+" + str(value)
        if self.name == "SUB":
            return "-" + str(value)
        if self.name == "TIMES":
            return +"*" + str(value)
        if self.name == "DIV":
            return "/" + str(value)
        if self.name == "POW":
            return "( )^" + str(value)
        if self.name == "SQRT":
            if value.value == 2:
                return "√( )"
            elif value.value == 3:
                return "∛( )"
            return f"[{str(value)}]√( )"

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
            if value.value == 2:
                return "\\textcolor{#a219e6}" + "{\\sqrt{\\phantom{a}}}"
            return "\\textcolor{#a219e6}" + (
                f"\\sqrt[{value.totex()}]" + "{\\phantom{a}}"
            ).join("{}")


class ETOperatorNode(ETNode):
    def __init__(self, type: ETOperatorType, value: Any):
        self.type = type
        self.value = value

    def __repr__(self):
        return "⇓" + self.type.torich(self.value)

    def totex(self, align=True):
        return "&\\Downarrow".replace("&", "&" * align) + self.type.totex(self.value)


class ETTextNode(ETNode):
    def __init__(self, result: str, color=None):
        super().__init__(result)
        self.color = color

    def __repr__(self):
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
        return f"Substitute {self.old} with {self.new}"

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
        return f"{self.result}" + "❌✅"[self.state]

    def totex(self, align):
        return "&" * align + self.result.totex(0) + "❌✅"[self.state]


class ETSteps:
    def __init__(self, data=None):
        self.data = data if data is not None else []
        self.history = [self.data]
        self.idx = [0]

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
        return "\n".join(
            str(step if isinstance(step, ETNode) else ETSteps(step))
            for step in self.data
        )

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


steps = ETSteps()
