from enum import Enum
from typing import Any


class ETNode:
    def __init__(self, result, description=None):
        self.result = result
        self.description = description
        self.prev = None
        self.next = None

    def _tex(self):
        return self.result.totex()

    def totex(self):
        res = self._tex()
        if not self.prev:
            res = "\\begin{aligned}" + res
        if not self.next:
            return res + "\\end{aligned}"
        return res + "\\\\" + self.next.totex()


class ETBranchNode(ETNode):
    def __init__(self, result, horizontal=False, description=None):
        super().__init__(result, description)
        self.result = list(map(ETNode, result))
        self.horizontal = horizontal

    def _tex(self):
        if any(x.next for x in self.result):
            res = (i.totex().join(("&\\boxed{", "}")) for i in self.result)
            if self.horizontal:
                return "&" + ("\\quad ").join(res)
            return "\\\\".join(res)
        return "&" + ",\\quad ".join(i.totex() for i in self.result)


class ETOperatorType(Enum):
    ADD = 0
    SUB = 1
    DIV = 2
    TIMES = 4
    POW = 5
    SQRT = 6

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
    def __init__(self, type: ETOperatorType, value: Any, description=None):
        self.type = type
        self.value = value
        self.prev = None
        self.next = None

    def _tex(self):
        return "&\\Downarrow" + self.type.totex(self.value)


class ETTextNode(ETNode):
    def _tex(self):
        return self.result
