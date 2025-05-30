from functools import lru_cache
from datatypes import Term, Number, Variable, Comparison, System, ETNode
from . import operators
from .nodes import Binary, Unary
from .parser import AST


class Interpreter:
    """
    Evaluates an AST (can be a Unary, Binary, or atomic value)
    Kept as a class to support setting variable values in the future
    """

    _eval_trace: ETNode = None
    print_frac_auto = True

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(
            "Direct instantiation of Interpreter is not allowed. Use Interpreter.eval(...)"
        )

    @classmethod
    @lru_cache
    def eval(
        cls,
        node: None | Unary | Binary | Number | Variable,
    ) -> Term | Comparison | System | tuple | None:
        if node is None:
            return
        if type(node) is str:
            return cls.eval(AST(node))
        if isinstance(node, (Number, Variable)):
            return Term(value=node)
        if isinstance(node, frozenset):
            return System(cls.eval(i) for i in node)
        if isinstance(node, tuple):
            return node

        oper = node.oper.type.name.lower()

        if isinstance(node, Unary):
            return getattr(operators, oper)(cls.eval(node.value))
        left = node.left
        right = cls.eval(node.right)
        if oper != "solve":  # Do not convert lhs to Term when solving
            left = cls.eval(left)
        return getattr(operators, oper)(left, right)

    @classmethod
    def log_step(cls, step: ETNode):
        # print("saving", step.result)
        if not cls._eval_trace:
            cls._eval_trace = step
        else:
            step.prev = cls._eval_trace
            cls._eval_trace.next = step
            cls._eval_trace = step

    @classmethod
    def render_steps_tex(cls) -> str:
        node = cls._eval_trace
        if not node:
            return ""
        while node.prev:
            node = node.prev
        return node.totex()

    @classmethod
    def reset_steps(cls):
        cls._eval_trace = None
