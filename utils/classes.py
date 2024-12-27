from functools import singledispatchmethod


class number: ...


class variable: ...


class product: ...


class polynomial: ...


class term: ...


class dispatch(singledispatchmethod):
    def __init__(self, method):
        return super().__init__(staticmethod(method))

    def register(self, cls):
        def wrapper(method):
            return self.dispatcher.register(cls, staticmethod(method))

        return wrapper


class Proxy:
    def __init__(self, value):
        self.value = value
        self._fake = eval(type(value.value).__name__.lower())

    @property
    def __class__(self):
        return self._fake
