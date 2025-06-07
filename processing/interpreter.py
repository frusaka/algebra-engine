from datatypes import Term, Number, Variable, Comparison, System
from . import operators
from .nodes import Binary, Unary
from .tokens import TokenType
from .parser import AST


class Interpreter:
    """
    Evaluates an AST (can be a Unary, Binary, or atomic value)
    Kept as a class to support setting variable values in the future
    """

    _instance = None

    def __init__(self, print_frac_auto=True):
        if Interpreter._instance is not None:
            raise RuntimeError("Interpreter is a singleton. Use Interpreter.instance()")
        self._eval_trace = None
        self.head = None
        self.print_frac_auto = print_frac_auto
        Interpreter._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            Interpreter()
        return cls._instance

    def eval(
        self, node: None | Unary | Binary | Number | Variable, autosolve=True
    ) -> Term | Comparison | System | tuple | None:
        if node is None:
            return
        if type(node) is str:
            return self.eval(AST(node), autosolve)
        if isinstance(node, (Number, Variable)):
            return Term(value=node)
        if isinstance(node, frozenset):
            res = System(self.eval(i, 0) for i in node)
            if not autosolve:
                return res
            vars = sorted(set(Variable(i) for i in str(res) if i.isalpha()), key=str)
            return operators.solve(tuple(map(Variable, vars)), res)

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operators, oper)(self.eval(node.value))
        left = node.left
        right = self.eval(node.right, 0)
        if oper != "solve":
            left = self.eval(left, 0)
            if (
                autosolve
                and TokenType[oper.upper()].value // 1 == 4
                and len(var := set(i for i in str(right) + str(left) if i.isalpha()))
                == 1
            ):
                return operators.solve(
                    Variable(var.pop()), getattr(operators, oper)(left, right)
                )
        return getattr(operators, oper)(left, right)
