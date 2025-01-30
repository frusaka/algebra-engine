from dataclasses import dataclass
from .solutions import Solutions
from .polynomial import Polynomial
from .product import Product
from .bases import Atomic
from .number import Number
from .variable import Variable
from .term import Term
from utils import quadratic, quadratic_formula


@dataclass
class Equation(Atomic):
    left: Term
    right: Term | Solutions

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
            return (self.reverse_div(Term(self.left.coef)))[value]
        if self.left.exp != 1:
            exp = Term() / Term(value=self.left.exp)
            if value in exp:
                raise NotImplementedError("Cannot isolate variable from exponent")
            return (self**exp)[value]

        if isinstance(self.left.value, Polynomial):
            # Brute-force factorization
            t = self.left / Term(value=value, exp=self.left.get_exp(value))
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
                    return (self * Term(value=i.value, exp=i.exp).inv)[value]
                # Term is in radical form
                elif exp.denominator != 1:
                    self -= self.left - i
                    print(self)
                    return (self ** Term(Number(exp.denominator)))[value]

            # Solving using the quadratic formuala
            if (res := quadratic(self, value)) is not None:
                res = Equation(Term(value=value), quadratic_formula(*res))
                print(res)
                return res

            if remove:
                return self.reverse_sub(remove)[value]

            # Solving by factoring coefficients
            _, left = Term.rationalize(self.right, self.left)
            if left != self.left:
                return (self.reverse_div((left / self.left) ** -Term()))[value]

        # Isolation by division
        if isinstance(self.left.value, Product):
            for t in self.left.value:
                exp = t.exp_const()
                if not value in t or exp < 0:
                    return self.reverse_div(t)[value]

        return self

    def __neg__(self):
        return Equation(-self.left, -self.right)

    def __add__(self, value: Term):
        self.show_operation("+", value)
        return Equation(self.left + value, self.right + value)

    def __sub__(self, value: Term):
        self.show_operation("-", value)
        return Equation(self.left - value, self.right - value)

    def __mul__(self, value: Term):
        self.show_operation("*", value)
        return Equation(self.left * value, self.right * value)

    def __truediv__(self, value: Term):
        self.show_operation("/", value)
        return Equation(self.left / value, self.right / value)

    def __pow__(self, value: Term):
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

    def reverse_sub(self, value: Term):
        """Make the logging of inverse subtration look natural"""
        if value.to_const() > 0:
            return self - value
        return self + -value

    def reverse_div(self, value: Term):
        """Make the logging of inverse division look natural"""
        if value.denominator.value != 1:
            return self * value.inv
        return self / value

    def show_operation(self, operator: str, value: Term):
        """A convinent method to show the user the solving process"""
        print(self)
        print(" " * str(self).index("="), operator + " ", value, sep="")
