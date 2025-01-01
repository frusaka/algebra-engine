from processing.tokens import TokenType
from processing.operators import SYMBOLS, Unary, Binary


class Parser:
    def __init__(self, tokens):
        self.tokens = self.prefix(tokens)

    def advance(self):
        try:
            self.curr = next(self.tokens)
        except StopIteration:
            self.curr = None

    @staticmethod
    def operator_error(oper):
        oper = SYMBOLS.get(oper.type.name)
        raise SyntaxError(f"operator '{oper}' has inadequate operands")

    @staticmethod
    def paren_error():
        raise SyntaxError("unmatched parenthesis")

    def parse(self):
        self.advance()
        if self.curr is None:
            return
        if self.curr.type in (TokenType.VAR, TokenType.NUMBER):
            return self.curr.value
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

    def postfix(self, tokens):
        stack = []
        # NOTE: Reversing the tokens reverses the parentheses
        for token in reversed(list(tokens)):
            if token.type in (TokenType.NUMBER, TokenType.VAR):
                yield token
            # Opening parenthesis
            elif token.type is TokenType.RPAREN:
                stack.append(token)
            # closing parenthesis
            elif token.type is TokenType.LPAREN:
                if not stack:
                    self.paren_error()
                while stack[-1].type != TokenType.RPAREN:
                    yield stack.pop()
                    if not stack:
                        self.paren_error()
                stack.pop()
            # An operator
            else:
                if not stack:
                    self.paren_error()
                if token.type is TokenType.POW:
                    while (
                        token.priority <= stack[-1].priority
                        or stack[-1].type is TokenType.NEG
                    ):
                        yield stack.pop()
                else:
                    while token.priority < stack[-1].priority:
                        yield stack.pop()
                stack.append(token)
        for i in stack:
            if i.type is TokenType.RPAREN:
                self.paren_error()
        yield from reversed(stack)

    def prefix(self, tokens):
        return reversed(list(self.postfix(tokens)))
