"""Highly composable wrapping decorators."""

from __future__ import annotations

from typing import Callable, Generic, Optional, Type, TypeVar

from attrs import frozen
from funcs.decorators import wraps
from typing_aliases import AnyError, AsyncCallable, NormalError
from typing_extensions import ParamSpec, final

from wraps.either import Either
from wraps.future import Future
from wraps.future_either import FutureEither
from wraps.future_option import FutureOption
from wraps.future_result import FutureResult
from wraps.option import Null, Option, Some
from wraps.result import Error, Ok, Result

__all__ = (
    # option
    "WrapOption",
    "WrapOptionAwait",
    "wrap_option",
    "wrap_option_await",
    "wrap_optional",
    # result
    "WrapResult",
    "WrapResultAwait",
    "wrap_result",
    "wrap_result_await",
    # future
    "wrap_future",
    # future option
    "wrap_future_option",
    # future result
    "wrap_future_result",
    # future either
    "wrap_future_either",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)

L = TypeVar("L", covariant=True)
R = TypeVar("R", covariant=True)

ET = TypeVar("ET", bound=AnyError)
FT = TypeVar("FT", bound=AnyError)


@final
@frozen()
class WrapOption(Generic[ET]):
    """Wraps functions returning `T` into functions returning [`Option[T]`][wraps.option.Option].

    Errors are handled via returning [`Null()`][wraps.option.Null] on `error` of `error_type`,
    wrapping the resulting `value` into [`Some(value)`][wraps.option.Some].

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

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapOption[FT]:
        return cls(error_type)  # type: ignore

    def __call__(self, function: Callable[P, T]) -> Callable[P, Option[T]]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(function(*args, **kwargs))

            except self.error_type:
                return Null()

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapOption[FT]:
        return self.create(error_type)


wrap_option = WrapOption(NormalError)
"""An instance of [`WrapOption[ET]`][wraps.wraps.WrapOption] with `error_type` set to
[`NormalError`][funcs.typing.NormalError].
"""


@final
@frozen()
class WrapOptionAwait(Generic[ET]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Option[T]`][wraps.option.Option].

    Errors are handled via returning [`Null()`][wraps.option.Null] on `error` of `error_type`,
    wrapping the resulting `value` into [`Some(value)`][wraps.option.Some].

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

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapOptionAwait[FT]:
        return cls(error_type)  # type: ignore

    def __call__(self, function: AsyncCallable[P, T]) -> AsyncCallable[P, Option[T]]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(await function(*args, **kwargs))

            except self.error_type:
                return Null()

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapOptionAwait[FT]:
        return self.create(error_type)


wrap_option_await = WrapOptionAwait(NormalError)
"""An instance of [`WrapOptionAwait[ET]`][wraps.wraps.WrapOptionAwait] with `error_type` set to
[`NormalError`][funcs.typing.NormalError].
"""


def wrap_optional(optional: Optional[T]) -> Option[T]:
    return Null() if optional is None else Some(optional)


@final
@frozen()
class WrapResult(Generic[ET]):
    """Wraps functions returning `T` into functions returning
    [`Result[T, ET]`][wraps.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.result.Error] on `error`
    of `error_type`, wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

    Example:
        ```python
        wrap_value_error = WrapResult(ValueError)

        @wrap_value_error
        def parse(string: str) -> int:
            return int(string)

        assert parse("256").is_ok()
        assert parse("uwu").is_error()
        ```
    """

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapResult[FT]:
        return cls(error_type)  # type: ignore

    def __call__(self, function: Callable[P, T]) -> Callable[P, Result[T, ET]]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, ET]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapResult[FT]:
        return self.create(error_type)


wrap_result = WrapResult(NormalError)
"""An instance of [`WrapResult[ET]`][wraps.wraps.WrapResult] with `error_type` set to
[`NormalError`][funcs.typing.NormalError].
"""


@final
@frozen()
class WrapResultAwait(Generic[ET]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Result[T, ET]`][wraps.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.result.Error] on `error`
    of `error_type`, wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

    Example:
        ```python
        wrap_value_error_await = WrapResultAwait(ValueError)

        @wrap_value_error_await
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_ok()
        assert (await parse("uwu")).is_error()
        ```
    """

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapResultAwait[FT]:
        return cls(error_type)  # type: ignore

    def __call__(self, function: AsyncCallable[P, T]) -> AsyncCallable[P, Result[T, ET]]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, ET]:
            try:
                return Ok(await function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapResultAwait[FT]:
        return self.create(error_type)


wrap_result_await = WrapResultAwait(NormalError)
"""An instance of [`WrapResultAwait[ET]`][wraps.wraps.WrapResultAwait] with `error_type` set to
[`NormalError`][funcs.typing.NormalError].
"""


def wrap_future(function: AsyncCallable[P, T]) -> Callable[P, Future[T]]:
    """Wraps an asynchronous `function` returning `T` into a function
    returning [`Future[T]`][wraps.future.Future].

    Example:
        ```python
        @wrap_future
        async def function() -> int:
            return 42

        string = "42"

        result = await function().map_future(str)

        assert result == string
        ```

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        return Future(function(*args, **kwargs))

    return wrap


def wrap_future_option(function: AsyncCallable[P, Option[T]]) -> Callable[P, FutureOption[T]]:
    """Wraps an asynchronous `function` returning [`Option[T]`][wraps.option.Option] into a function
    returning [`FutureOption[T]`][wraps.future_option.FutureOption].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureOption[T]:
        return FutureOption(function(*args, **kwargs))

    return wrap


def wrap_future_result(function: AsyncCallable[P, Result[T, E]]) -> Callable[P, FutureResult[T, E]]:
    """Wraps an asynchronous `function` returning [`Result[T, E]`][wraps.result.Result]
    into a function returning [`FutureResult[T, E]`][wraps.future_result.FutureResult].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureResult[T, E]:
        return FutureResult(function(*args, **kwargs))

    return wrap


def wrap_future_either(function: AsyncCallable[P, Either[L, R]]) -> Callable[P, FutureEither[L, R]]:
    """Wraps an asynchronous `function` returning [`Either[L, R]`][wraps.either.Either]
    into a function returning [`FutureEither[L, R]`][wraps.future_either.FutureEither].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureEither[L, R]:
        return FutureEither(function(*args, **kwargs))

    return wrap
