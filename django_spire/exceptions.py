from __future__ import annotations


class DjangoSpireError(Exception):
    pass


class DjangoSpireConfigurationError(DjangoSpireError):
    pass


class DjangoSpireInvalidClassStringError(DjangoSpireError):
    pass


class DjangoSpireMissingRequiredAppError(DjangoSpireError):
    pass
