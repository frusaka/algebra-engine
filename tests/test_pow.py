import pytest
from datatypes.nodes import Const, Var, Add, Mul, Pow

# Test will require avoiding circluar verification
# Currently, all the nodes perform evaluation at construction.
# This makes side to side comparison a bit circular, but gets the job done.
# This file is skipped because variable power rules are not implemented
