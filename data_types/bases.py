from fractions import Fraction


class Base:
    """Base class for all atomic objects"""

    def like(self, other):
        if type(self) is not type(other):
            return 0
        if hasattr(self, "imag"):
            return 1
        return self == other

    @staticmethod
    def poly_pow(b, a):
        b = b.value
        if b.exp != 1:
            return
        res = type(a)()
        for i in b.value:
            res *= a**i
        return res


class Unknown:
    """
    A small class that prevents comparsions between unknowns.
    This class should be removed and better alternatives developed
    """

    def __eq__(self, value):
        return super().__eq__(value) and type(value) is type(self)

    def __gt__(self, value):
        return False

    def __lt__(self, value):
        return False

    def __ge__(self, value):
        return self == value

    def __le__(self, value):
        return self == value
