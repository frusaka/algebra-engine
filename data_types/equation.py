from dataclasses import dataclass
from .polynomial import Polynomial
from .product import Product
from .bases import Base
from .number import Number
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
        # NOTE: if val>0:... checks are not necessary, they just make the solving process look natural
        print(self)
        if not (value in self.left or value in self.right):
            raise KeyError(f"Variable '{value}' not found")

        # Rewrite the equation to put the target variable on the left
        if value in self.right and not value in self.left:
            self = Equation(self.right, self.left)
            print(self)

        # Moving target terms to the left
        if isinstance(self.right.value, Polynomial):
            if value in self.right:
                if self.right.exp != 1:
                    return self.reverse_sub(self.right)[value]
                for t in self.right.value:
                    if value in t:
                        return self.reverse_sub(t)[value]

        if self.left.coef != 1:
            return (self / AlgebraObject(self.left.coef))[value]
        if self.left.exp != 1:
            exp = AlgebraObject() / AlgebraObject(value=self.left.exp)
            if value in exp:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self**exp)[value]

        if isinstance(self.left.value, Polynomial):
            # Brute-force factorization
            t = self.left / AlgebraObject(value=value)
            if not value in t:
                return self.reverse_div(t)[value]

            for i in self.left.value:
                # Isolation by subtraction
                if not value in i:
                    return self.reverse_sub(i)[value]

                # Term is in a fraction
                if isinstance(i.value, Product):
                    for t in i.value:
                        if t.exp_const() < 0:
                            return (self * (AlgebraObject() / t))[value]
                elif i.exp_const() < 0:
                    return (
                        self
                        * (AlgebraObject() / AlgebraObject(value=i.value, exp=i.exp))
                    )[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                exp = t.exp_const()
                if not value in t or exp < 0:
                    return self.reverse_div(t)[value]

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

    def reverse_sub(self, value: AlgebraObject):
        if value.tovalue() > 0:
            return self - value
        return self + -value

    def reverse_div(self, value: AlgebraObject):
        if value.exp_const() < 0:
            return self * (AlgebraObject() / value)
        return self / value

    def show_operation(self, operator: str, value: AlgebraObject):
        print(self)
        print(" " * str(self).index("="), operator + " ", value, sep="")
