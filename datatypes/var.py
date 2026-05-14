from .base import Node


class Var(Node, str):
    def __repr__(self):
        return str(self)

    def __copy__(self):
        return Var(str(self))


__all__ = ["Var"]
