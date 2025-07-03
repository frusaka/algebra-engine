import eel
from pylatexenc.latexwalker import (
    LatexWalker,
    LatexCharsNode,
    LatexNode,
    LatexGroupNode,
    LatexMacroNode,
)

from processing import Interpreter
from utils.constants import TEXTOKEN, SYMBOLS
from datatypes.nodes import steps


@eel.expose
def evaluate(latex: str):
    print(latex)
    nodes, _, _ = LatexWalker(
        latex.replace("\\left(", "(")
        .replace("\\right)", ")")
        .replace("\\placeholder{}", "")
    ).get_latex_nodes()
    try:
        res = processor.eval("".join(map(stringify_node, nodes))).totex(0)
    except Exception as e:
        res = "\\textcolor{#d7170b}{\\text{$}}".replace("$", repr(e))
    res = "\\\\".join((steps.totex(), res))
    steps.clear()
    return res


def stringify_node(node: LatexNode) -> str:
    if node.__class__ is LatexCharsNode:
        return node.chars
    if node.__class__ is LatexGroupNode:
        return "".join(map(stringify_node, node.nodelist)).join("()")
    if node.__class__ is LatexMacroNode:
        if not node.nodeargd.argnlist:
            return SYMBOLS[TEXTOKEN[node.macroname]]
        if node.macroname == "sqrt":
            a, b = node.nodeargd.argnlist
            if a is None:
                return stringify_node(b).join("()") + "^0.5"
            a, b = map(stringify_node, (a, b))
            return b.join("()") + f"^(1/{a.join('()')})"
        return (
            SYMBOLS[TEXTOKEN[node.macroname]]
            .join(map(stringify_node, node.nodeargd.argnlist))
            .join("()")
        )
    return ""


processor = Interpreter(False)

eel.init("web")
eel.start("index.html")
