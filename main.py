import webview

from parsing.lexer import Lexer
from parsing.parser import Parser
from utils.steps import explain, set_verbosity


class API:
    def evaluate(self, expr):
        res, steps, success = "", [], True
        try:
            res = Parser(Lexer(expr).tokenize()).parse()
            steps = explain(res, False)
            if steps:
                steps = steps.toJSON()
            else:
                steps = []
            res = res.totex().join(("$$", "$$")) if hasattr(res, "totex") else str(res)
        except Exception as e:
            # raise
            success = False
            res = repr(e)
        return {"output": res, "success": success, "steps": steps}


if __name__ == "__main__":
    set_verbosity(True)
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
