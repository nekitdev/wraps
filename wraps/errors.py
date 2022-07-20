from typing import Generic, TypeVar

from typing_extensions import Never

__all__ = ("Panic", "panic", "OptionShortcut", "ResultShortcut")


class Panic(BaseException):
    """Represents the panic as an error.

    Panics should not be explicitly handled in general, therefore [`Panic`][wraps.errors.Panic]
    is derived from [`BaseException`][BaseException] instead of [`Exception`][Exception].
    """


def panic(message: str) -> Never:
    raise Panic(message)


E = TypeVar("E", covariant=True)

OPTION_SHORTCUT_WITHOUT_DECORATOR = "the `Q` operator used without `@option_shortcut` decorator"
RESULT_SHORTCUT_WITHOUT_DECORATOR = "the `Q` operator used without `@result_shortcut` decorator"


class OptionShortcut(Exception):
    def __init__(self) -> None:
        super().__init__(OPTION_SHORTCUT_WITHOUT_DECORATOR)


class ResultShortcut(Exception, Generic[E]):
    def __init__(self, error: E) -> None:
        super().__init__(RESULT_SHORTCUT_WITHOUT_DECORATOR)

        self._error = error

    @property
    def error(self) -> E:
        return self._error
