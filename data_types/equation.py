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
        print(self)
        if not (value in self.left or value in self.right):
            raise KeyError(f"Variable '{value}' not found")
        # Put the term being solved for on the left and everything else on the right
        if value in self.right and not value in self.left:
            self = Equation(self.right, self.left)
            print(self)

        # Moving target terms to the left
        if isinstance(self.right.value, Polynomial):
            for t in self.right.value:
                if value in t:
                    if self.right.exp != 1:
                        raise NotImplementedError(
                            f"Error isolating term from Polynomial with an exponent of {self.right.exp}"
                        )
                    return (self - t)[value]

        if self.left.coef != 1:
            return (self / AlgebraObject(self.left.coef))[value]
        if self.left.exp != 1:
            return (self ** (AlgebraObject() / AlgebraObject(value=self.left.exp)))[
                value
            ]

        # Isolation by subtraction
        if isinstance(self.left.value, Polynomial):
            for t in self.left.value:
                if not value in t:
                    return (self - t)[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                if not value in t or t.exp != 1:
                    if isinstance(t.value, Polynomial):
                        return self.ensure_cancels(t, self.left)
                    return (self / t)[value]

        # Isolation by factorization
        if isinstance(self.left.value, Polynomial):
            t = self.left / AlgebraObject(value=value)
            if not value in t:
                return (self / t)[value]
            # Term is in a fraction
            for i in self.left.value:
                if value in i:
                    if isinstance(i.value, Product):
                        for t in i.value:
                            if (t.exp if isinstance(t.exp, Number) else t.exp.coef) < 0:
                                # Backend implementation not yet properly working if denominator is a Polynomial
                                if isinstance(t.value, Polynomial):
                                    return self.ensure_cancels(t, i)[value]
                                return (self * (AlgebraObject() / t))[value]
                    elif (i.exp if isinstance(i.exp, Number) else i.exp.coef) < 0:
                        return (
                            self
                            * (
                                AlgebraObject()
                                / AlgebraObject(value=i.value, exp=i.exp)
                            )
                        )[value]
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

    def ensure_cancels(self, term: AlgebraObject, product: AlgebraObject):
        """
        A workaround for the current Polynomial division and multiplication logic
        It does not factor itself out in cases of fractions
        """
        j = AlgebraObject() / AlgebraObject(value=term.value, exp=term.exp)
        c = AlgebraObject(product.coef)
        left, right = (self.left - product) * j, (self * j).right
        res = product.value.copy()
        res.remove(term)
        if res:
            if len(res) == 1:
                left += res.pop() * c
            else:
                left += AlgebraObject(c.value, Product(res))
        else:
            left += c
        return Equation(left, right)

    def show_operation(self, operator: str, value: AlgebraObject):
        print(self)
        print(" " * str(self).index("="), operator + " ", value, sep="")
