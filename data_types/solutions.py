from .collection import Collection
from .algebraobject import AlgebraObject


class Solutions(Collection):
    def __add__(self, value: AlgebraObject):
        return Solutions(t + value for t in self)

    def __sub__(self, value: AlgebraObject):
        return Solutions(t - value for t in self)

    def __mul__(self, value: AlgebraObject):
        return Solutions(t * value for t in self)

    def __truediv__(self, value: AlgebraObject):
        return Solutions(t / value for t in self)

    def __pow__(self, value: AlgebraObject):
        return Solutions(t**value for t in self)

    def __str__(self) -> str:
        return ", ".join(str(t) for t in self).join("{}")

    @property
    def value(self):
        return self
