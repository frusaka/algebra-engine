class Step:
    def __init__(self, rule, before, final_before, after, children=None):
        self.rule = rule
        self.before = before
        self.final_before = final_before
        self.after = after
        self.children = children or []

    def __repr__(self):
        def _str(step, depth):
            if not step.children:
                return f"{step.rule}: {step.before} → {step.after}"
            res = f"{step.rule}: {step.before}"
            for idx, i in enumerate(step.children, 1):
                res += "\n" + "   " * depth + str(idx) + ". " + _str(i, depth + 1)
            res += (
                "\n"
                + "   " * depth
                + str(idx + 1)
                + f". {step.final_before} → {step.after}"
            )
            return res

        return _str(self, 1)
