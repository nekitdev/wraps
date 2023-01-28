from typing import Generic, TypeVar

from typing_extensions import Never

from wraps.typing import AnyException

__all__ = ("Panic", "panic", "EarlyOption", "EarlyResult")


class Panic(AnyException):
    """Represents the panic as an error.

    Panics should not be explicitly handled in general, therefore [`Panic`][wraps.errors.Panic]
    is derived from [`AnyException`][wraps.typing.AnyException] instead of [`Exception`][Exception].
    """


def panic(message: str) -> Never:
    raise Panic(message)


E = TypeVar("E", covariant=True)

EARLY_OPTION_WITHOUT_DECORATOR = "the `early` operator used without `@early_option` decorator"
EARLY_RESULT_WITHOUT_DECORATOR = "the `early` operator used without `@early_result` decorator"


class EarlyOption(AnyException):
    def __init__(self) -> None:
        super().__init__(EARLY_OPTION_WITHOUT_DECORATOR)


class EarlyResult(AnyException, Generic[E]):
    def __init__(self, error: E) -> None:
        super().__init__(EARLY_RESULT_WITHOUT_DECORATOR)

        self._error = error

    @property
    def error(self) -> E:
        return self._error
