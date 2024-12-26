class number: ...


class variable: ...


class product: ...


class polynomial: ...


class term: ...


class Proxy:
    def __init__(self, value):
        self.value = value
        self._fake = eval(type(value.value).__name__.lower())

    @property
    def __class__(self):
        return self._fake
