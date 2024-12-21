from .bases import *
from .term import Term
from .expressions import *


for cls in (Variable, Number, Expression, Factor):
    Base.register_term_operations(cls)
