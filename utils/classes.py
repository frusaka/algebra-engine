class number:
    pass


class variable:
    pass


class fraction:
    pass


class factor:
    pass


class polynomial:
    pass


class term:
    pass


class Proxy:
    def __init__(self, value, fake):
        self.value = value
        self._fake = fake

    @property
    def __class__(self):
        return self._fake
