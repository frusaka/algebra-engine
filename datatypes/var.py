from .base import Node


class Var(Node, str):
    def __repr__(self):
        return str(self)


__all__ = ["Var"]
