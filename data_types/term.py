from dataclasses import dataclass
from .bases import *
from .expressions import *
from utils.utils import clean


@dataclass(order=True, frozen=True)
class Term(Base):
    coef: Number = Number(1)
    value: Base = Number(1)
    exp: Base = Number(1)

    def __hash__(self):
        return hash((self.__class__, self.coef, self.value, self.exp))

    def __str__(self):
        res = ""
        if not isinstance(self.value, Number):
            if abs(self.coef) != 1:
                res = str(self.coef)
                if "/" in res:
                    res = res.join("()")
            elif self.coef == -1:
                res = "-"
        else:
            res = str(self.value)
            if "/" in res and self.exp != 1:
                res = res.join("()")
        if not isinstance(self.value, Number):
            res += str(self.value)

        if isinstance(self.exp, Number):
            if self.exp == 1:
                return res
            if self.exp < 0:
                return "{0}/{1}".format(
                    self.coef.numerator,
                    Term(Number(self.coef.denominator), self.value, abs(self.exp)),
                )
            if self.exp.denominator != 1:
                if self.coef != 1:
                    return "{0}({1})".format(
                        "-" if self.coef == -1 else self.coef,
                        Term(value=self.value, exp=self.exp),
                    )
                if self.exp.numerator != 1:
                    res = "{0}^{1}".format(res, self.exp.numerator)
                return "{0}√{1}".format(self.exp.denominator, res)
        return "{0}^{1}".format(res, self.exp)

    @clean
    def __add__(a, b):
        if a.value == 0:
            return b
        if b.value == 0:
            return a
        if not a.like(b):
            return Term(value=Polynomial([a, b]))
        return Base.add(a, b)

    @clean
    def __sub__(a, b):
        return a + -b

    @clean
    def __mul__(a, b):
        if v := Base.mul(a, b):
            return v
        if a.exp.like(b.exp):
            return Term(
                a.coef * b.coef,
                Factor(
                    [Term(value=a.value, exp=a.exp), Term(value=b.value, exp=b.exp)]
                ),
            )

    @clean
    def __truediv__(a, b):
        return a * b ** -Term()

    @clean
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
        return self * Term(value=Number(-1))

    def like(self, other, exp=1):

        if (
            not isinstance(other, Term)
            or not self.exp.like(other.exp)
            or not isinstance(other.value, type(self.value))
            or (exp)
            and (
                self.exp != other.exp
                or isinstance(other.value, Number)
                and (self.exp != 1 or other.exp != 1)
            )
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
