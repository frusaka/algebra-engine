from rich.console import Console

from datatypes.base import Node
from solving.eval_trace import ETSteps
from processing import parser
import cProfile
import pstats

from processing.lexer import Lexer
import utils

print = Console().print

while True:
    try:
        inp = parser.Parser(Lexer(input("Expression > ")).generate_tokens())
        # with cProfile.Profile() as profile:
        res = inp.parse()
        if isinstance(res, Node):
            res = res.simplify()
        if ETSteps.data:
            print(ETSteps.torich())
        print(res)
        # results = pstats.Stats(profile)
        # results.sort_stats(pstats.SortKey.CUMULATIVE)
        # results.print_stats(15)
    except Exception as e:
        if ETSteps.data:
            print(ETSteps.torich())
        # raise
        print(repr(e))
    ETSteps.clear()
