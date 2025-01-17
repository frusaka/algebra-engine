from dataclasses import dataclass
from .solutions import Solutions
from .polynomial import Polynomial
from .product import Product
from .bases import Base
from .number import Number
from .variable import Variable
from .algebraobject import AlgebraObject


@dataclass
class Equation(Base):
    left: AlgebraObject
    right: AlgebraObject | Solutions

    def __hash__(self):
        return hash((Equation, self.left, self.right))

    def __str__(self):
        return "{0} = {1}".format(self.left, self.right)

    def __getitem__(self, value: Variable):
        """
        This method will be called when solving for a variable.
        Extraneous solutions, fnfinite solutions, or no solution cases are not in check
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
        if value in self.right:
            return self.reverse_sub(self.right)[value]

        if self.left.coef != 1:
            return (self.reverse_div(AlgebraObject(self.left.coef)))[value]
        if self.left.exp != 1:
            exp = AlgebraObject() / AlgebraObject(value=self.left.exp)
            if value in exp:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self**exp)[value]

        if isinstance(self.left.value, Polynomial):
            # Brute-force factorization
            t = self.left / AlgebraObject(value=value, exp=self.left.get_exp(value))
            if not value in t:
                return self.reverse_div(t)[value]
            remove = None
            for i in self.left.value:
                if not value in i:
                    remove = i  # Not moving it yet, need to check for quadratics
                    continue
                # Term is in a fraction
                if isinstance(i.value, Product):
                    for t in i.value:
                        if t.exp_const() < 0:
                            return (self * t.inv)[value]
                elif (exp := i.exp_const()) < 0:
                    return (self * AlgebraObject(value=i.value, exp=i.exp).inv)[value]
                # Term is in radical form
                elif exp.denominator != 1:
                    self -= self.left - i
                    print(self)
                    return (self ** AlgebraObject(Number(exp.denominator)))[value]

            # Solving using the quadratic formuala
            if (res := self.solve_quadratic(value)) is not self:
                return res

            if remove:
                return self.reverse_sub(remove)[value]

            # Solving by factoring coefficients
            _, left = AlgebraObject.rationalize(self.right, self.left)
            if left != self.left:
                return (self.reverse_div((left / self.left) ** -AlgebraObject()))[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                exp = t.exp_const()
                if not value in t or exp < 0:
                    return self.reverse_div(t)[value]

        return self

    def __neg__(self):
        return Equation(-self.left, -self.right)

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
        rhs = self.right**value
        if (
            value.exp == 1
            and isinstance(value.value, Number)
            and value.value.denominator == 2
        ):
            # Assumes the left-hand side containes the variable being solved for
            # Otherwise it would be {-x, x} = {+n, -n}
            # sqrt(x) = +-..
            rhs = Solutions({rhs, -rhs})
        return Equation(self.left**value, rhs)

    def solve_quadratic(self, value: Variable):
        """
        Given that the lhs is a Polynomial,
        check whether it can be considered quadratic in terms of `value` and solve
        """
        a, b = None, None
        x = AlgebraObject(value=value)
        for t in self.left.value:  # Must be a Polynomial
            v = t / x
            # Checks to detect a Quadratice
            # One term that when divided by x cancels the x
            if value not in v:
                if b:
                    return self
                b = v
                bx = t
            # One term that when divided by x^2 cancels the x
            elif value not in (v := v / x):
                if a:
                    return self
                a = v
                ax_2 = t
            # Should otherwise not contain x if not divisible by x or x^2
            elif value in t:
                return self
        # Not a quadratic
        if not a or not b:
            return self
        # Make the rhs 0
        if self.right.value:
            self = self.reverse_sub(self.right)
            print(self)
        # The rest of the boys, can even be another Polynomial
        c = self.left - (ax_2 + bx)
        # Apply the formula
        res = Equation(x, self.quadratic_formula(a, b, c))
        print(res)
        return res

    @staticmethod
    def quadratic_formula(a: AlgebraObject, b: AlgebraObject, c: AlgebraObject):
        """Apply the quadratic formula: (-b ± (b^2 - 4ac))/2a"""
        print("Quadratic(a={0}, b={1}, c={2})".format(a, b, c))
        rhs = (
            b ** AlgebraObject(Number(2)) - AlgebraObject(Number(4)) * a * c
        ) ** AlgebraObject(value=Number("1/2"))
        den = AlgebraObject(Number(2)) * a
        res = {(-b + rhs) / den, (-b - rhs) / den}
        if len(res) == 1:
            return res.pop()
        return Solutions(res)

    def reverse_sub(self, value: AlgebraObject):
        """Make the logging of inverse subtration look natural"""
        if value.to_const() > 0:
            return self - value
        return self + -value

    def reverse_div(self, value: AlgebraObject):
        """Make the logging of inverse division look natural"""
        if value.denominator.value != 1:
            return self * value.inv
        return self / value

    def show_operation(self, operator: str, value: AlgebraObject):
        """A convinent method to show the user the solving process"""
        print(self)
        print(" " * str(self).index("="), operator + " ", value, sep="")
