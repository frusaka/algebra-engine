import webview
from pylatexenc.latexwalker import (
    LatexWalker,
    LatexCharsNode,
    LatexNode,
    LatexGroupNode,
    LatexMacroNode,
)


from parsing import parser
from utils.constants import TEXTOKEN, SYMBOLS
from solving.eval_trace import ETSteps


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


class API:
    def evaluate(self, latex: str, mode="solve"):
        nodes, _, _ = LatexWalker(
            latex.replace("\\left(", "(")
            .replace("\\right)", ")")
            .replace("\\placeholder{}", "")
        ).get_latex_nodes()
        try:
            res = parser.eval("".join(map(stringify_node, nodes)), mode == "solve")
            if mode != "solve":
                res = getattr(res, mode)()
            res = res.totex() if hasattr(res, "totex") else str(res)
        except Exception as e:
            res = "\\textcolor{#d7170b}{\\text{$}}".replace("$", repr(e))
        steps = ETSteps.toHTML()
        ETSteps.clear()
        return [steps, res.join(("$$", "$$"))]


if __name__ == "__main__":
    webview.create_window("Algebra Engine", "web/index.html", js_api=API())
    webview.start()
