from processing.tokens import TokenType
from processing.operators import SYMBOLS, Unary, Binary
from data_types import Term


class Parser:
    def __init__(self, prefix_tokens):
        self.tokens = iter(prefix_tokens)

    def advance(self):
        try:
            self.curr = next(self.tokens)
        except StopIteration:
            self.curr = None

    def operator_error(self, oper):
        oper = SYMBOLS.get(oper.type.name)
        raise SyntaxError(f"operator '{oper}' has inadequate operands")

    def parse(self):
        self.advance()
        if self.curr is None:
            return
        if self.curr.type in (TokenType.VAR, TokenType.NUMBER):
            return Term(value=self.curr.value)
        oper = self.curr
        left = self.parse()
        if not left:
            self.operator_error(oper)
        if oper.type in (TokenType.NEG, TokenType.POS):
            return Unary(oper, left)
        right = self.parse()
        if not right:
            self.operator_error(oper)
        return Binary(oper, left, right)
