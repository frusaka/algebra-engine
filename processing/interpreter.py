from functools import lru_cache
from data_types import Term, Number, Variable, Comparison, System
from . import operators
from .operators import Binary, Unary


class Interpreter:
    """
    Evaluates an AST (can be a Unary, Binary, or atomic value)
    Kept as a class to support setting variable values in the future
    """

    @lru_cache
    def eval(
        self, node: None | Unary | Binary | Number | Variable
    ) -> Term | Comparison | System | tuple | None:
        if node is None:
            return
        if isinstance(node, (Number, Variable)):
            if str(node) == "i":
                return Term(value=Number(complex(imag=1)))
            return Term(value=node)
        if isinstance(node, frozenset):
            return System(self.eval(i) for i in node)
        if isinstance(node, tuple):
            return node

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operators, oper)(self.eval(node.value))
        left = node.left
        right = self.eval(node.right)
        if oper != "solve":  # Do not convert lhs to Term when solving
            left = self.eval(left)
        return getattr(operators, oper)(left, right)
