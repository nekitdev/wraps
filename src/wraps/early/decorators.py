"""Early return decorators."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from funcs.decorators import wraps
from typing_extensions import ParamSpec

from wraps.early.errors import EarlyOption, EarlyResult
from wraps.option import NULL, Option
from wraps.result import Err, Result

if TYPE_CHECKING:
    from wraps.typing import (
        OptionAsyncCallable,
        OptionCallable,
        ResultAsyncCallable,
        ResultCallable,
    )

__all__ = (
    # option
    "early_option",
    "early_option_await",
    # result
    "early_result",
    "early_result_await",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)


def early_option(function: OptionCallable[P, T]) -> OptionCallable[P, T]:
    """Decorates the `function` returning [`Option[T]`][wraps.option.Option]
    to handle *early returns* via the `early` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return function(*args, **kwargs)

        except EarlyOption:
            return NULL

    return wrap


def early_option_await(function: OptionAsyncCallable[P, T]) -> OptionAsyncCallable[P, T]:
    """Decorates the asynchronous `function` returning [`Option[T]`][wraps.option.Option]
    to handle *early returns* via the `early` (`?` in Rust) operator.

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The asynchronous wrapping function.
    """

    @wraps(function)
    async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return await function(*args, **kwargs)

        except EarlyOption:
            return NULL

    return wrap


def early_result(function: ResultCallable[P, T, E]) -> ResultCallable[P, T, E]:
    """Decorates the `function` returning [`Result[T, E]`][wraps.result.Result]
    to handle *early returns* via the `early` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return function(*args, **kwargs)

        except EarlyResult[E] as early:
            return Err(early.error)

    return wrap


def early_result_await(function: ResultAsyncCallable[P, T, E]) -> ResultAsyncCallable[P, T, E]:
    """Decorates the asynchronous `function` returning [`Result[T, E]`][wraps.result.Result]
    to handle *early returns* via the `early` (`?` in Rust) operator.

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The asynchronous wrapping function.
    """

    @wraps(function)
    async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return await function(*args, **kwargs)

        except EarlyResult[E] as early:
            return Err(early.error)

    return wrap
