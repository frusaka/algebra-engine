from parsing import parser
from parsing.lexer import FUNCTIONS
from utils import steps

import re

from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.padding import Padding
from textual import on, work
from textual.widgets import Input, Header, Footer, Static, Collapsible
from textual.containers import VerticalScroll
from textual.app import App
from textual.validation import Validator
from rich.highlighter import ReprHighlighter


def determine(val):
    if isinstance(val, Panel):
        res = determine(val.renderable)
        res.styles.border = "solid", val.border_style
        return res
    if isinstance(val, Padding):
        return determine(val.renderable)
    if isinstance(val, Group):
        if isinstance(val.renderables[0], str):
            title = Text.from_markup(val.renderables[0])
            highlighter.highlight(title)
            if isinstance(val.renderables[1], Padding):
                vals = val.renderables[1:]
                vals = vals[0].renderable.renderables + vals[1:]
                res = Collapsible(
                    *(determine(v) for v in vals),
                    title=title,
                    collapsed=val.collapsed,
                )
                res.compact = Text.from_markup(val.step_header)
                highlighter.highlight(res.compact)
                res.org_title = title
                if val.collapsed:
                    res.title = res.compact
                return res
            return Collapsible(
                *(determine(v) for v in val.renderables[1:]),
                title=title,
                collapsed=False,
            )

        return Collapsible(
            *(determine(v) for v in val.renderables), title="", collapsed=False
        )
    if isinstance(val, steps.step.Step):
        return determine(val.__rich__())
    text = Text.from_markup(str(val))
    highlighter.highlight(text)
    return Static(text)


highlighter = ReprHighlighter()


from textual.app import App, ComposeResult
from textual.widgets import Input
from textual.suggester import Suggester


class ExprSuggester(Suggester):
    async def get_suggestion(self, value: str):
        if not value:
            return
        match = re.search(r"([a-zA-Z_]+)$", value)

        if not match:
            return None

        last = match.group(1)

        for fn in FUNCTIONS:
            if fn.lower().startswith(last):
                start = match.start(1)
                return value[:start] + fn.lower()


class ExprValidator(Validator):
    def validate(self, value: str):
        if not value:
            return self.success()
        try:
            parser.AST(value)
            return self.success()
        except Exception as e:
            res = Text(e.args[0])
            highlighter.highlight(res)
            return self.failure(
                f"[bold red]{type(e).__name__}:[/bold red] " + e.args[0]
            )


class AlgebraEngine(App):
    BINDINGS = [("shift+delete", "clear_history", "Clear History")]

    def compose(self) -> ComposeResult:
        with Header():
            title = Static("[bold magenta]Algebra Engine[/bold magenta]", expand=True)
            title.styles.text_align = "center"
            yield title
        yield VerticalScroll(
            VerticalScroll(id="history"),
            # RichLog(id="log"),
            Input(
                placeholder="Enter math here",
                id="input",
                highlighter=highlighter,
                validators=[ExprValidator()],
                suggester=ExprSuggester(),
                validate_on=["submitted"],
            ),
        )
        yield Footer()

    def on_mount(self):
        self.query_one(Input).focus()

    @work(thread=True)
    def evaluate(self, expr: str):
        try:
            res = parser.parse(expr)
            self.call_from_thread(self.add_step, steps.explain(res), expr)
        except Exception as e:
            self.call_from_thread(self.add_step, steps.explain(e, maxdepth=None), expr)

    def action_clear_history(self):
        self.query_one("#history", VerticalScroll).remove_children()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted):
        if not event.value:
            return
        if not event.validation_result.is_valid:
            event.input.tooltip = event.validation_result.failure_descriptions[0]
            self.action_notify(
                event.validation_result.failure_descriptions[0], severity="error"
            )
            return
        event.input.tooltip = None
        self.evaluate(event.value).run()

    def add_step(self, step, input: str):
        history = self.query_one("#history", VerticalScroll)
        history.mount(determine(step))

        history.scroll_end()

    @on(Collapsible.Expanded)
    def toggle_expanded(self, event: Collapsible.Expanded):
        if hasattr(event.collapsible, "org_title"):
            event.collapsible.title = event.collapsible.org_title
            history = self.query_one("#history", VerticalScroll)
            history.scroll_to_widget(event.collapsible, top=True)

    @on(Collapsible.Collapsed)
    def toggle_collapsed(self, event: Collapsible.Collapsed):
        if hasattr(event.collapsible, "compact"):
            event.collapsible.title = event.collapsible.compact


if __name__ == "__main__":
    steps.set_verbosity(True)
    ae = AlgebraEngine()
    ae.run()
