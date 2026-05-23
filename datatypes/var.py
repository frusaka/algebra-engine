from .base import Expr


class Var(Expr, str):
    def __repr__(self):
        return str(self)

    def __copy__(self):
        return Var(str(self))


__all__ = ["Var"]
