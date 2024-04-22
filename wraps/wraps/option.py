from __future__ import annotations

from typing import Callable, Generic, Optional, Type, final

from attrs import frozen
from funcs.decorators import wraps
from typing_aliases import AnyError, AsyncCallable, NormalError
from typing_extensions import ParamSpec, TypeVar

from wraps.primitives.option import NULL, Option, Some
from wraps.primitives.typing import OptionAsyncCallable, OptionCallable

__all__ = (
    "WrapOption",
    "WrapOptionAwait",
    "wrap_option",
    "wrap_option_await",
    "wrap_optional",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)

E = TypeVar("E", bound=AnyError)
F = TypeVar("F", bound=AnyError)


@final
@frozen()
class WrapOption(Generic[E]):
    """Wraps functions returning `T` into functions returning [`Option[T]`][wraps.primitives.option.Option].

    Errors are handled via returning [`NULL`][wraps.primitives.option.NULL] on `error` of
    [`error_type`][wraps.wraps.option.WrapOption.error_type],
    wrapping the resulting `value` into [`Some(value)`][wraps.primitives.option.Some].

    Example:
        ```python
        wrap_value_error = WrapOption(ValueError)

        @wrap_value_error
        def parse(string: str) -> int:
            return int(string)

        assert parse("256").is_some()
        assert parse("uwu").is_null()
        ```
    """

    error_type: Type[E]
    """The error type to handle."""

    @classmethod
    def create(cls, error_type: Type[F]) -> WrapOption[F]:
        return cls(error_type)  # type: ignore[arg-type, return-value]

    def __call__(self, function: Callable[P, T]) -> OptionCallable[P, T]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(function(*args, **kwargs))

            except self.error_type:
                return NULL

        return wrap

    def __getitem__(self, error_type: Type[F]) -> WrapOption[F]:
        return self.create(error_type)


wrap_option = WrapOption(NormalError)
"""An instance of [`WrapOption[NormalError]`][wraps.wraps.option.WrapOption]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapOptionAwait(Generic[E]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Option[T]`][wraps.primitives.option.Option].

    Errors are handled via returning [`NULL`][wraps.primitives.option.NULL] on `error` of `error_type`,
    wrapping the resulting `value` into [`Some(value)`][wraps.primitives.option.Some].

    Example:
        ```python
        wrap_value_error_await = WrapOptionAwait(ValueError)

        @wrap_value_error_await
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_some()
        assert (await parse("uwu")).is_null()
        ```
    """

    error_type: Type[E]
    """The error type to handle."""

    @classmethod
    def create(cls, error_type: Type[F]) -> WrapOptionAwait[F]:
        return cls(error_type)  # type: ignore[arg-type, return-value]

    def __call__(self, function: AsyncCallable[P, T]) -> OptionAsyncCallable[P, T]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(await function(*args, **kwargs))

            except self.error_type:
                return NULL

        return wrap

    def __getitem__(self, error_type: Type[F]) -> WrapOptionAwait[F]:
        return self.create(error_type)


wrap_option_await = WrapOptionAwait(NormalError)
"""An instance of [`WrapOptionAwait[NormalError]`][wraps.wraps.option.WrapOptionAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""


def wrap_optional(optional: Optional[T]) -> Option[T]:
    """Wraps [`Optional[T]`][typing.Optional] into [`Option[T]`][wraps.primitives.option.Option].

    If the argument is [`None`][None], [`NULL`][wraps.primitives.option.NULL] is returned.
    Otherwise the `value` (of type `T`) is wrapped into [`Some(value)`][wraps.primitives.option.Some].

    Arguments:
        optional: The optional value to wrap.

    Returns:
        The wrapped option.
    """
    return NULL if optional is None else Some(optional)
