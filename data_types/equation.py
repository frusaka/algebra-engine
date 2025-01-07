from dataclasses import dataclass
from .collection import Collection
from .polynomial import Polynomial
from .product import Product
from .bases import Base
from .variable import Variable
from .algebraobject import AlgebraObject


@dataclass
class Equation(Base):
    left: AlgebraObject
    right: AlgebraObject

    def __hash__(self):
        return hash((Equation, self.left, self.right))

    def __str__(self):
        return "{0} = {1}".format(self.left, self.right)

    def __getitem__(self, value: Variable):
        """
        This method will be called when solving for a variable
        """
        # Put the term being solved for on the left and everything else on the right
        if self.search(self.right, value) and (not self.search(self.left, value)):
            self = Equation(self.right, self.left)
            print(self)
        if self.left.coef != 1:
            self /= AlgebraObject(self.left.coef)
        if self.left.exp != 1:
            self **= AlgebraObject() / AlgebraObject(value=self.left.exp)

        # Moving target terms to the left
        if isinstance(self.left.value, Polynomial):
            for t in self.left.value:
                if not self.search(t, value):
                    return (self - t)[value]
        if isinstance(self.right.value, Polynomial):
            for t in self.right.value:
                if self.search(t, value):
                    if self.right.exp != 1:
                        raise NotImplementedError(
                            f"Error isolating term from Polynomial with an exponent of {self.right.exp}"
                        )
                    return (self - t)[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                if not self.search(t, value):
                    return (self / t)[value]

        # Isolation by factorization
        if isinstance(self.left.value, Polynomial):
            val = self.left / AlgebraObject(value=value)
            if (
                not isinstance(val.value, Polynomial)
                # Try make sure long division was used
                or val != self.left * val ** -AlgebraObject()
            ) and not self.search(val, value):
                return (self / val)[value]

        if not self.search(self.left, value):
            raise KeyError(f"Variable '{value}' not found")
        return self

    def __neg__(self):
        return Equation(-self.left, -self.right)

    def __pos__(self):
        return self

    def __add__(self, value: AlgebraObject):
        self.show_operation("+", value)
        return Equation(self.left + value, self.right + value)

    def __sub__(self, value: AlgebraObject):
        self.show_operation("-", value)
        return Equation(self.left - value, self.right - value)

    def __mul__(self, value: AlgebraObject):
        self.show_operation("*", value)
        return Equation(self.left * value, self.right * value)

    def __truediv__(self, value: AlgebraObject):
        self.show_operation("/", value)
        return Equation(self.left / value, self.right / value)

    def __pow__(self, value: AlgebraObject):
        self.show_operation("^", value)
        return Equation(self.left**value, self.right**value)

    def show_operation(self, operator: str, value: AlgebraObject):
        print(self)
        print(" " * str(self).index("="), operator + " ", value, sep="")

    def search(self, item: AlgebraObject, value: Variable):
        if item.value == value:
            return True
        if isinstance(item.value, Collection):
            return any(self.search(t, value) for t in item.value)
        if isinstance(item.exp, AlgebraObject) and self.search(item.exp, value):
            raise NotImplementedError("Cannot get variable from exponent")
        return False
