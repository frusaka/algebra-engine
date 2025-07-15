import cProfile
from functools import reduce
import itertools
import pstats
from timeit import timeit


from datatypes.nodes import *
from utils import factor
import utils

# from sympy import factor

# from sympy import Symbol as Var


x = Var("x")
y = Var("y")
a = Var("a")
c = Var("c")
b = Var("b")


from sympy import Poly, groebner, roots, solve, symbols

x = symbols("x")

print(roots(Poly(x**3 - 2 * x**2 + 4 * x - 5, x)))

# org = (
#     (a**2 + b**2 + 2 * a * b)
#     * (a - 2 * b) ** 2
#     * (x**3 - 8) ** 2
#     * (b - 2 * x) ** 3
#     * (x - b) ** 5
# ).expand()

# with cProfile.Profile(builtins=False) as profile:
#     factored = factor(org)
# print(factored)
# results = pstats.Stats(profile)
# results.sort_stats(pstats.SortKey.CUMULATIVE)
# results.print_stats(50)
# org = ((52 * x**3 + 70 * x**2 - 312 * x - 420) * (a**3 - b**3)).expand()
# print(factor(org))

# org = ((2 * x**2 - 8) * (x**3 - 8) ** 4 * (x**2 + x - 56) * (x - 5) * (x - 1)).expand()

# factored = factor(org)

# print(factored, factored.expand() == org)
# org = ((x + 1) * (3 * x + 7)).expand()

# factored = factor(org)

# print(factored, factored.expand() == org)


# org = -3 * y**2 - 3 * x * y + 2 * a * y + 2 * a * x
# factored = factor(org)
# print(factored, factored.expand() == org)


# org = a**4 - b**4
# print(org, org.simplify())
