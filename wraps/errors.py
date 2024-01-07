"""Various errors."""

from typing import Generic, TypeVar

from typing_aliases import AnyError

__all__ = ("EarlyOption", "EarlyResult")

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
