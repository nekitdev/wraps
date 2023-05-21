"""Panics and early return errors."""

from typing import Generic, TypeVar

from typing_aliases import AnyError
from typing_extensions import Never

__all__ = ("Panic", "panic", "EarlyOption", "EarlyResult")


class Panic(AnyError):
    """Represents panics as errors.

    Panics should not be explicitly handled in general, therefore [`Panic`][wraps.errors.Panic]
    is derived from [`AnyError`][funcs.typing.AnyError].
    """


def panic(message: str) -> Never:
    """Panics with the given `message`.

    Arguments:
        message: The message to panic with.

    Raises:
        Panic: Always raised.
    """
    raise Panic(message)


E = TypeVar("E", covariant=True)

EARLY_OPTION_WITHOUT_DECORATOR = "the `early` operator used without `@early_option` decorator"
EARLY_RESULT_WITHOUT_DECORATOR = "the `early` operator used without `@early_result` decorator"


class EarlyOption(AnyError):
    def __init__(self) -> None:
        super().__init__(EARLY_OPTION_WITHOUT_DECORATOR)


class EarlyResult(AnyError, Generic[E]):
    def __init__(self, error: E) -> None:
        super().__init__(EARLY_RESULT_WITHOUT_DECORATOR)

        self._error = error

    @property
    def error(self) -> E:
        return self._error
