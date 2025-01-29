import operator
from data_types import Term, Equation, Number, Variable
from processing.operators import Binary, Unary


class Interpreter:
    """
    Evaluates an AST (can be a Unary, Binary, or atomic value)
    Kept as a class to support setting variable values in the future
    """

    def eval(self, node: None | Unary | Binary | Number | Variable) -> Term | None:
        if node is None:
            return
        if isinstance(node, (Number, Variable)):
            if isinstance(node, Variable) and str(node) == "i":
                return Term(value=Number(complex(imag=1)))
            return Term(value=node)

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operator, oper)(self.eval(node.value))

        left, right = self.eval(node.left), self.eval(node.right)

        if oper == "root":
            return operator.pow(right, Term() / left)
        if oper == "eqn":
            return Equation(left, right)
        if oper == "getitem":
            return right[left.value]

        return getattr(operator, oper)(left, right)
