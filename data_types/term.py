from dataclasses import dataclass
from .bases import *
from .expressions import *
from utils.utils import flatten


@dataclass(order=True)
class Term(Base):
    coef: Number
    value: Base
    exp: Base

    def __init__(
        self, coef: Number = Number(1), value: Base = Number(1), exp: Base = Number(1)
    ):
        self.coef = coef
        self.value = value
        self.exp = exp
        if self.coef == 0:
            self.value = Number(1)
            self.exp = self.value
        elif self.exp == 0:
            self.value, self.exp = (Number(1),) * 2
        super().__init__()

    def __hash__(self):
        return hash((self.__class__, self.coef, self.value, self.exp))

    def __str__(self):
        # if self.coef.denominator != 1:
        #     return "{0}/{1}".format(
        #         Term(Number(self.coef.numerator), self.value, self.exp),
        #         self.coef.denominator,
        #     )
        res = ""
        if not isinstance(self.value, Number):
            if abs(self.coef) != 1:
                if self.coef.denominator != 1:
                    res += "(" + str(self.coef) + ")"
                else:
                    res += str(self.coef)
            elif self.value == -1:
                res += "-"

        res += str(self.value)
        if type(self.exp) is Number:
            if self.exp == 1:
                return res
            if self.exp < 0:
                return "{0}/{1}".format(
                    self.coef, Term(value=self.value, exp=abs(self.exp))
                )
            if self.exp.denominator != 1:
                if self.coef != 1:
                    return "{0}({1})".format(
                        "-" if self.coef == -1 else self.coef,
                        Term(value=self.value, exp=self.exp),
                    )
                if self.exp.numerator != 1:
                    res = "{0}^{1}".format(res, self.exp.numerator)
                return "({0}√{1})".format(self.exp.denominator, res)
        return "{0}^{1}".format(res, self.exp)

    @flatten
    def __add__(a, b):
        return Base.add(a, b) or Term(value=Expression([a, b]))

    @flatten
    def __sub__(a, b):
        return -b + a

    @flatten
    def __mul__(a, b):
        c = a.coef * b.coef
        ta = Term(value=a.value, exp=a.exp)
        tb = Term(value=b.value, exp=b.exp)
        if (
            not a.exp.like(b.exp)
            or isinstance(a.exp, Number)
            and a.exp.denominator != 1
        ):
            return Term(c, Factor([ta, tb]), a.exp)

        return Base.mul(a, b) or Term(c, value=Factor([ta, tb]))

    @flatten
    def __truediv__(a, b):
        return a * Term(Number(1) / b.coef, b.value, b.exp) ** -Term()

    @flatten
    def __pow__(a, b):
        if not a.exp.like(b.exp):
            return Term(a.coef, a.value, a.exp * b.exp)
        c = a.exp
        if not isinstance(a.exp, Term):
            c = Term(value=a.exp)
        return Base.pow(a, b) or Term(a.coef, a.value, b * c)

    def __pos__(self):
        return self

    def __neg__(self):
        if isinstance(self.value, Expression):
            return Term(value=Expression(-term for term in self.value), exp=self.exp)
        if isinstance(self.value, Number):
            return Term(value=-self.value, exp=self.exp)
        return Term(-self.coef, self.value, self.exp)

    def like(self, other, exp=1):

        if (
            # not isinstance(other, type(self))
            not isinstance(other.value, type(self.value))
            or (exp and self.exp != other.exp)
        ):
            return 0
        if not isinstance(other.value, Number):
            return self.value == other.value
        return 1

    @singledispatchmethod
    def add(self, b, a):
        pass

    @singledispatchmethod
    def mul(self, b, a):
        pass

    @singledispatchmethod
    def pow(self, b, a):
        pass
