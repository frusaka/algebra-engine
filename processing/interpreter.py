import operator
from data_types import AlgebraObject, Number, Variable
from processing.operators import Unary


class Interpreter:
    def eval(self, node):
        if node is None:
            return
        if isinstance(node, (Number, Variable)):
            if isinstance(node, Variable) and str(node) == "i":
                return AlgebraObject(value=Number(imag=1))
            return AlgebraObject(value=node)

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operator, oper)(self.eval(node.value))

        left, right = self.eval(node.left), self.eval(node.right)

        if oper == "root":
            return operator.pow(right, AlgebraObject() / left)

        return getattr(operator, oper)(left, right)
