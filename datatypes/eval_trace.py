from enum import Enum
from typing import Any


class ETNode:
    def __init__(self, result, description=None):
        self.result = result
        self.description = description
        self.prev = None
        self.next = None

    def totex(self):
        res = self.result.totex()
        if not self.prev:
            res = "\\begin{aligned}" + res
        if not self.next:
            return res + "\\end{aligned}"
        return res + "\\\\" + self.next.totex()


class ETBranchNode(ETNode):
    def __init__(self, result, description=None):
        super().__init__(result, description)
        self.result = list(map(ETNode, result))

    def totex(self):
        if any(x.next for x in self.result):
            res = "&" + "\\quad".join(
                i.totex().join(("\\boxed{", "}")) for i in self.result
            )
        else:
            res = "&" + ",\\quad".join(i.totex() for i in self.result)
        if self.next:
            return res + "\\\\" + self.next.totex()
        return res + "\\end{aligned}"


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

    def totex(self):
        res = "&\\Downarrow" + self.type.totex(self.value)
        if self.next:
            return res + "\\\\" + self.next.totex()
        return res + "\\end{aligned}"


class ETTextNode(ETNode):
    def totex(self):
        if not self.next:
            return self.result + "\\end{aligned}"
        return self.result + "\\\\" + self.next.totex()
