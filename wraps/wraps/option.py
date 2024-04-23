from __future__ import annotations

from typing import Callable, Generic, Optional, Type, final

from attrs import field, frozen
from funcs.decorators import wraps
from typing_aliases import AnyError, AsyncCallable, NormalError
from typing_extensions import ParamSpec, TypeVar

from wraps.primitives.option import NULL, Option, Some
from wraps.primitives.typing import OptionAsyncCallable, OptionCallable
from wraps.wraps.error_types import ErrorTypes, expect_error_types, expect_error_types_runtime

__all__ = (
    # decorators
    "WrapOption",
    "WrapOptionAwait",
    # decorator factories
    "wrap_option_on",
    "wrap_option_await_on",
    # decorator instances
    "wrap_option",
    "wrap_option_await",
    # wrapping functions
    "wrap_optional",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)

E = TypeVar("E", bound=AnyError)


@final
@frozen()
class WrapOption(Generic[E]):
    """Wraps functions returning `T` into functions returning
    [`Option[T]`][wraps.primitives.option.Option].

    Errors are handled via returning [`NULL`][wraps.primitives.option.NULL] on `error` of
    [`error_types`][wraps.wraps.option.WrapOption.error_types], wrapping the resulting
    `value` into [`Some(value)`][wraps.primitives.option.Some].
    """

    error_types: ErrorTypes[E] = field(converter=expect_error_types_runtime)
    """The error types to handle. See [`ErrorTypes[E]`][wraps.wraps.error_types.ErrorTypes]."""

    def __call__(self, function: Callable[P, T]) -> OptionCallable[P, T]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(function(*args, **kwargs))

            except self.error_types:
                return NULL

        return wrap


def wrap_option_on(*error_types: Type[E]) -> WrapOption[E]:
    """Creates [`WrapOption[E]`][wraps.wraps.option.WrapOption] decorators.

    Warning:
        This function will panic if no error types are provided!

    Example:
        ```python
        @wrap_option_on(ValueError)
        def parse(string: str) -> int:
            return int(string)

        assert parse("256").is_some()
        assert parse("uwu").is_null()
        ```

    Arguments:
        *error_types: The error types to handle.

    Returns:
        The [`WrapOption[E]`][wraps.wraps.option.WrapOption] decorator created.
    """
    return WrapOption(expect_error_types(error_types))


wrap_option = wrap_option_on(NormalError)
"""An instance of [`WrapOption[NormalError]`][wraps.wraps.option.WrapOption]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapOptionAwait(Generic[E]):
    """Wraps asynchronous functions returning `T` into functions returning
    [`Option[T]`][wraps.primitives.option.Option].

    Errors are handled via returning [`NULL`][wraps.primitives.option.NULL] on `error` of
    [`error_types`][wraps.wraps.option.WrapOptionAwait.error_types], wrapping the resulting
    `value` into [`Some(value)`][wraps.primitives.option.Some].
    """

    error_types: ErrorTypes[E] = field(converter=expect_error_types_runtime)
    """The error types to handle. See [`ErrorTypes[E]`][wraps.wraps.error_types.ErrorTypes]."""

    def __call__(self, function: AsyncCallable[P, T]) -> OptionAsyncCallable[P, T]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(await function(*args, **kwargs))

            except self.error_types:
                return NULL

        return wrap


def wrap_option_await_on(*error_types: Type[E]) -> WrapOptionAwait[E]:
    """Creates [`WrapOptionAwait[E]`][wraps.wraps.option.WrapOptionAwait] decorators.

    Warning:
        This function will panic if no error types are provided!

    Example:
        ```python
        @wrap_option_await_on(ValueError)
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_some()
        assert (await parse("uwu")).is_null()
        ```

    Arguments:
        *error_types: The error types to handle.

    Returns:
        The [`WrapOptionAwait[E]`][wraps.wraps.option.WrapOptionAwait] decorator created.
    """
    return WrapOptionAwait(expect_error_types(error_types))


wrap_option_await = wrap_option_await_on(NormalError)
"""An instance of [`WrapOptionAwait[NormalError]`][wraps.wraps.option.WrapOptionAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""


def wrap_optional(optional: Optional[T]) -> Option[T]:
    """Wraps [`Optional[T]`][typing.Optional] into [`Option[T]`][wraps.primitives.option.Option].

    If the argument is [`None`][None], [`NULL`][wraps.primitives.option.NULL] is returned.
    Otherwise the `value` (of type `T`) is wrapped into
    [`Some(value)`][wraps.primitives.option.Some].

    Arguments:
        optional: The optional value to wrap.

    Returns:
        The wrapped option.
    """
    return NULL if optional is None else Some(optional)
