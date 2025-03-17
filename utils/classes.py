from functools import singledispatchmethod


class number: ...


class variable: ...


class product: ...


class polynomial: ...


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
        self._fake = CLASSES[value.value.__class__.__name__]

    @property
    def __class__(self):
        return self._fake

CLASSES = {"Number":number, "Variable":variable, "Product":product, "Polynomial":polynomial}