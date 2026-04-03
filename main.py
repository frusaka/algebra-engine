import webview

from parsing.lexer import Lexer
from parsing.parser import Parser
from solving.comparison import Comparison
from solving.eval_trace import ETSteps


class API:
    def evaluate(self, expr):
        Comparison.solve_for.cache_clear()
        ETSteps.clear()
        res, success = "", True
        try:
            res = Parser(Lexer(expr).tokenize()).parse()
            res = res.totex().join(("$$", "$$")) if hasattr(res, "totex") else str(res)
        except Exception as e:
            # raise
            success = False
            res = repr(e)
        steps = ETSteps.toJSON()
        return {"output": res, "success": success, "steps": steps}


if __name__ == "__main__":
    webview.create_window(
        "Algebra Engine",
        "web/dist/index.html",
        text_select=True,
        zoomable=True,
        width=650,
        height=600,
        min_size=(400, 400),
        js_api=API(),
    )
    webview.start()
