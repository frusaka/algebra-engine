from .base import Node
from . import nodes


class Var(Node, str):
    def __repr__(self):
        return str(self)


__all__ = ["Var"]
