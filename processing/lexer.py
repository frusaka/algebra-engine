from processing.tokens import Token, TokenType
from data_types import Number, Variable


class Lexer:
    OPERS = {
        "=": Token(TokenType.EQ),
        "≠": Token(TokenType.NE),
        ">": Token(TokenType.GT),
        "≥": Token(TokenType.GE),
        "<": Token(TokenType.LT),
        "≤": Token(TokenType.LE),
        "+": (Token(TokenType.ADD), Token(TokenType.POS)),
        "-": (Token(TokenType.SUB), Token(TokenType.NEG)),
        "*": Token(TokenType.MUL),
        "/": Token(TokenType.TRUEDIV),
        "^": Token(TokenType.POW),
        "√": Token(TokenType.ROOT),
        "(": Token(TokenType.LPAREN),
        ")": Token(TokenType.RPAREN),
    }

    def __init__(self, expr):
        self.expr = iter(expr.join("()"))
        self.advance()

    def advance(self):
        try:
            self.curr = next(self.expr)
        except StopIteration:
            self.curr = None

    def generate_tokens(self):
        was_num = 0
        while self.curr is not None:
            if self.curr in " \n\t":
                self.advance()
                continue
            if self.curr == "." or self.curr.isdigit():
                # Can be toggled off to experiment with other notations (prefix & postfix)
                if was_num:
                    # Implicit multiplication - Parenthesis or consecutive numbers numbers
                    yield self.OPERS["*"]
                yield self.generate_number()
                was_num = 1
                continue
            if self.curr.isalpha():
                if was_num:
                    # Implicit multiplication - Variable Coefficient
                    yield self.OPERS["*"]
                yield Token(TokenType.VAR, Variable(self.curr))
                was_num = 1
            elif self.curr in "+-":
                yield self.OPERS[self.curr][not was_num]
                was_num = 0
            elif self.curr in self.OPERS:
                if was_num and self.curr == "(":
                    # Implicit multiplication - Product
                    yield self.OPERS["*"]
                yield self.OPERS[self.curr]
                was_num = self.curr == ")"
            else:
                raise TypeError(f"illegal token '{self.curr}'")
            self.advance()

    def generate_number(self):
        decimals = 0
        number_str = ""
        while self.curr is not None and (self.curr == "." or self.curr.isdigit()):
            if self.curr == ".":
                decimals += 1
                if decimals > 1:
                    break
            number_str += self.curr
            self.advance()
        if number_str == ".":
            raise ValueError("decimal point needs atlest one digit")
        return Token(TokenType.NUMBER, Number(number_str))

    @staticmethod
    def paren_error():
        raise SyntaxError("unmatched parenthesis")

    def postfix(self):
        stack = []
        # NOTE: Reversing the tokens reverses the parentheses
        for token in reversed(list(self.generate_tokens())):
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
                    while token.priority <= stack[-1].priority:
                        yield stack.pop()
                else:
                    while token.priority < stack[-1].priority:
                        yield stack.pop()
                stack.append(token)
        for i in stack:
            if i.type is TokenType.RPAREN:
                self.paren_error()
        yield from reversed(stack)

    def prefix(self):
        return reversed(list(self.postfix()))
