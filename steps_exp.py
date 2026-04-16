from rich import print

from datatypes import *
from solving import solve
from solving.comparison import Comparison, CompRel
from step_tracking import eval_trace, explain, set_verbosity

x = Var("x")

set_verbosity(True)

# print(explain(x + 0))
# print(explain(x))
# print(explain(x**2))
# print(explain(x + 5 - 3))
# print(explain(3 * x / 2))
# print(explain((3 + x + x - 3 * x) * (x + x) + 5))
# print(
#     explain(
#         (
#             (
#                 (Const(26, 5) * x**3 + 7 * x**2 - Const(156, 5) * x - 42)
#                 / (Const(7, 2) + Const(13, 5) * x)
#             )
#         ).simplify()
#     )
# )
# print(explain((3 * (x + 6) - (x + 6) / 2) / (x + 6) ** 2))

# print(
#     explain(
#         Comparison((3 * (x + 6) - (x + 6) / 2) / (x + 6) ** 2, Const(12)).solve_for(x)
#     )
# )
# print(explain((Comparison(3 * x**5 - 5, Const(12)).solve_for(x))))
print(explain(Comparison((2 / x), Const(8)).solve_for(x)))
# print(eval_trace._steps)
