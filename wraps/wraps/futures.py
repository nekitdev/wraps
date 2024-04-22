from typing import TypeVar

from funcs.decorators import wraps
from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec

from wraps.futures.base import Future
from wraps.futures.either import FutureEither
from wraps.futures.option import FutureOption
from wraps.futures.result import FutureResult
from wraps.futures.typing.base import FutureCallable
from wraps.futures.typing.derived import (
    FutureEitherCallable,
    FutureOptionCallable,
    FutureResultCallable,
)
from wraps.primitives.typing import EitherAsyncCallable, OptionAsyncCallable, ResultAsyncCallable

__all__ = (
    "wrap_future",
    "wrap_future_option",
    "wrap_future_result",
    "wrap_future_either",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)

L = TypeVar("L", covariant=True)
R = TypeVar("R", covariant=True)


def wrap_future(function: AsyncCallable[P, T]) -> FutureCallable[P, T]:
    """Wraps an asynchronous `function` returning `T` into a function
    returning [`Future[T]`][wraps.futures.base.Future].

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


def wrap_future_option(function: OptionAsyncCallable[P, T]) -> FutureOptionCallable[P, T]:
    """Wraps an asynchronous `function` returning [`Option[T]`][wraps.primitives.option.Option] into a function
    returning [`FutureOption[T]`][wraps.futures.option.FutureOption].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureOption[T]:
        return FutureOption(function(*args, **kwargs))

    return wrap


def wrap_future_result(function: ResultAsyncCallable[P, T, E]) -> FutureResultCallable[P, T, E]:
    """Wraps an asynchronous `function` returning [`Result[T, E]`][wraps.primitives.result.Result]
    into a function returning [`FutureResult[T, E]`][wraps.futures.result.FutureResult].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureResult[T, E]:
        return FutureResult(function(*args, **kwargs))

    return wrap


def wrap_future_either(function: EitherAsyncCallable[P, L, R]) -> FutureEitherCallable[P, L, R]:
    """Wraps an asynchronous `function` returning [`Either[L, R]`][wraps.primitives.either.Either]
    into a function returning [`FutureEither[L, R]`][wraps.futures.either.FutureEither].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureEither[L, R]:
        return FutureEither(function(*args, **kwargs))

    return wrap
