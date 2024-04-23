from typing import Type, TypeVar

from annotated_types import MinLen
from typing_aliases import AnyError, DynamicTuple
from typing_extensions import Annotated, TypeIs

from wraps.panics import panic

__all__ = (
    "ErrorTypesMaybeEmpty",
    "ErrorTypes",
    "is_error_types",
    "expect_error_types",
    "expect_error_types_runtime",
)

E = TypeVar("E", bound=AnyError)

ErrorTypesMaybeEmpty = DynamicTuple[Type[E]]
"""Represents error types that may be empty.
`E` is bound to [`AnyError`][typing_aliases.AnyError].
"""

ErrorTypes = Annotated[ErrorTypesMaybeEmpty[E], MinLen(1)]
"""Represents non-empty error types. `E` is bound to [`AnyError`][typing_aliases.AnyError]."""


EXPECTED_ERROR_TYPES = "expected `ErrorTypes[E]` (non-empty `DynamicTuple[Type[E]]`), got {}"
expected_error_types = EXPECTED_ERROR_TYPES.format


def is_error_types(error_types: ErrorTypesMaybeEmpty[E]) -> TypeIs[ErrorTypes[E]]:
    """Checks if the `error_types` tuple provided is non-empty.

    Arguments:
        error_types: The tuple of error types to check.

    Returns:
        Whether the provided tuple is non-empty.
    """
    return len(error_types) >= 1


def expect_error_types(error_types_maybe_empty: ErrorTypesMaybeEmpty[E]) -> ErrorTypes[E]:
    """Expects error types provided to be non-empty.

    Warning:
        This function panics if the error types are empty.

    Arguments:
        error_types_maybe_empty: The error types to check.

    Raises:
        Panic: If the error types are empty.

    Returns:
        The error types if they are non-empty.
    """
    if is_error_types(error_types_maybe_empty):
        return error_types_maybe_empty

    panic(expected_error_types(error_types_maybe_empty))


def expect_error_types_runtime(error_types: ErrorTypes[E]) -> ErrorTypes[E]:
    """Same as [`expect_error_types`][wraps.wraps.error_types.expect_error_types],
    but for runtime checks only.
    """
    return expect_error_types(error_types)
