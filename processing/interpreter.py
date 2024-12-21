import operator
from data_types import Term, Number
from processing.operators import Unary


class Interpreter:
    def eval(self, node):
        if not node:
            return
        if isinstance(node, Term):
            return node

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operator, oper)(self.eval(node.value))

        left, right = self.eval(node.left), self.eval(node.right)

        if oper == "root":
            return operator.pow(right, Term(Number(1)) / left)

        return getattr(operator, oper)(left, right)
