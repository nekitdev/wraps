"""Early return errors used for propagation."""

from __future__ import annotations

from typing import Generic, TypeVar

from typing_aliases import AnyError

__all__ = ("EarlyOption", "EarlyResult")

E = TypeVar("E", covariant=True)

EARLY_OPTION_WITHOUT_DECORATOR = "the `early` operator used without `@early_option` decorator"
EARLY_RESULT_WITHOUT_DECORATOR = "the `early` operator used without `@early_result` decorator"


class EarlyOption(AnyError):
    """The internal error raised by the [`early`][wraps.option.OptionProtocol.early] method."""

    def __init__(self) -> None:
        super().__init__(EARLY_OPTION_WITHOUT_DECORATOR)


class EarlyResult(AnyError, Generic[E]):
    """The internal error raised by the [`early`][wraps.result.ResultProtocol.early] method."""

    def __init__(self, error: E) -> None:
        super().__init__(EARLY_RESULT_WITHOUT_DECORATOR)

        self._error = error

    @property
    def error(self) -> E:
        """The error to return early."""
        return self._error
