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


@eel.expose
def evaluate(latex: str):
    print(latex)
    nodes, _, _ = LatexWalker(
        latex.replace("\\left(", "(")
        .replace("\\right)", ")")
        .replace("\\placeholder{}", "")
    ).get_latex_nodes()
    try:
        res = Interpreter.eval("".join(map(stringify_node, nodes))).totex()
    except Exception as e:
        res = "\\textcolor{#d7170b}{\\text{$}}".replace("$", repr(e))
    steps = Interpreter.render_steps_tex()
    Interpreter.reset_steps()
    print(steps)
    return "\\\\".join((steps, res.replace("&", "")))


def stringify_node(node: LatexNode) -> str:
    if node.__class__ is LatexCharsNode:
        return node.chars
    if node.__class__ is LatexGroupNode:
        return "".join(map(stringify_node, node.nodelist)).join("()")
    if node.__class__ is LatexMacroNode:
        if not node.nodeargd.argnlist:
            return SYMBOLS[TEXTOKEN[node.macroname]]
        if node.macroname == "sqrt" and node.nodeargd.argnlist[0] is None:
            return (
                SYMBOLS[TEXTOKEN[node.macroname]]
                .join(("2", stringify_node(node.nodeargd.argnlist[1])))
                .join("()")
            )
        return (
            SYMBOLS[TEXTOKEN[node.macroname]]
            .join(map(stringify_node, node.nodeargd.argnlist))
            .join("()")
        )
    return ""


Interpreter.print_frac_auto = False

eel.init("web")
eel.start("index.html")
