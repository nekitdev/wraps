from __future__ import annotations

from typing import Callable, Generic, Type, TypeVar, final

from attrs import field, frozen
from funcs.decorators import wraps
from typing_aliases import AnyError, AsyncCallable, NormalError
from typing_extensions import ParamSpec

from wraps.primitives.result import Error, Ok, Result
from wraps.primitives.typing import ResultAsyncCallable, ResultCallable
from wraps.wraps.error_types import ErrorTypes, expect_error_types, expect_error_types_runtime

__all__ = (
    # decorators
    "WrapResult",
    "WrapResultAwait",
    # decorator factories
    "wrap_result_on",
    "wrap_result_await_on",
    # decorator instances
    "wrap_result",
    "wrap_result_await",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)

E = TypeVar("E", bound=AnyError)
F = TypeVar("F", bound=AnyError)


@final
@frozen()
class WrapResult(Generic[E]):
    """Wraps functions returning `T` into functions returning
    [`Result[T, E]`][wraps.primitives.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.primitives.result.Error] on `error` of
    [`error_types`][wraps.wraps.result.WrapResult.error_types], wrapping the resulting
    `value` into [`Ok(value)`][wraps.primitives.result.Ok].
    """

    error_types: ErrorTypes[E] = field(converter=expect_error_types_runtime)
    """The error types to handle. See [`ErrorTypes[E]`][wraps.wraps.error_types.ErrorTypes]."""

    def __call__(self, function: Callable[P, T]) -> ResultCallable[P, T, E]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_types as error:
                return Error(error)

        return wrap


def wrap_result_on(*error_types: Type[E]) -> WrapResult[E]:
    """Creates [`WrapResult[E]`][wraps.wraps.result.WrapResult] decorators.

    Warning:
        This function will panic if no error types are provided!

    Example:
        ```python
        @wrap_result_on(ValueError)
        def parse(string: str) -> int:
            return int(string)

        assert parse("128").is_ok()
        assert parse("owo").is_error()
        ```

    Arguments:
        *error_types: The error types to handle.

    Returns:
        The [`WrapResult[E]`][wraps.wraps.result.WrapResult] decorator created.
    """
    return WrapResult(expect_error_types(error_types))


wrap_result = wrap_result_on(NormalError)
"""An instance of [`WrapResult[NormalError]`][wraps.wraps.result.WrapResult]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapResultAwait(Generic[E]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Result[T, E]`][wraps.primitives.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.primitives.result.Error] on `error` of
    [`error_types`][wraps.wraps.result.WrapResult.error_types], wrapping the resulting
    `value` into [`Ok(value)`][wraps.primitives.result.Ok].
    """

    error_types: ErrorTypes[E] = field(converter=expect_error_types_runtime)
    """The error types to handle. See [`ErrorTypes[E]`][wraps.wraps.error_types.ErrorTypes]."""

    def __call__(self, function: AsyncCallable[P, T]) -> ResultAsyncCallable[P, T, E]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                return Ok(await function(*args, **kwargs))

            except self.error_types as error:
                return Error(error)

        return wrap


def wrap_result_await_on(*error_types: Type[E]) -> WrapResultAwait[E]:
    """Creates [`WrapResultAwait[E]`][wraps.wraps.result.WrapResultAwait] decorators.

    Warning:
        This function will panic if no error types are provided!

    Example:
        ```python
        @wrap_result_await_on(ValueError)
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("128")).is_ok()
        assert (await parse("owo")).is_error()
        ```

    Arguments:
        *error_types: The error types to handle.

    Returns:
        The [`WrapResultAwait[E]`][wraps.wraps.result.WrapResultAwait] decorator created.
    """
    return WrapResultAwait(expect_error_types(error_types))


wrap_result_await = wrap_result_await_on(NormalError)
"""An instance of [`WrapResultAwait[NormalError]`][wraps.wraps.result.WrapResultAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""
