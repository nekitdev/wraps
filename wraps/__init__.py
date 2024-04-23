"""Meaningful and safe wrapping types.

This library implements several types:

- [`Option[T]`][wraps.primitives.option.Option] for optional values;
- [`Result[T, E]`][wraps.primitives.result.Result] for error handling;
- [`Either[L, R]`][wraps.primitives.either.Either] for either values;
- [`Future[T]`][wraps.futures.base.Future] for asynchronous abstractions.

The following types are implemented for convenience:

- [`Future[Option[T]] -> FutureOption[T]`][wraps.futures.option.FutureOption];
- [`Future[Result[T, E]] -> FutureResult[T, E]`][wraps.futures.result.FutureResult];
- [`Future[Either[L, R]] -> FutureEither[L, R]`][wraps.futures.either.FutureEither].

The library also provides various decorators to wrap functions in order to return the types above.
"""

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.11.0"

from wraps.early import (
    EarlyOption,
    EarlyResult,
    early_option,
    early_option_await,
    early_result,
    early_result_await,
)
from wraps.futures import Future, FutureEither, FutureOption, FutureResult
from wraps.panics import Panic, panic
from wraps.primitives import (
    NULL,
    Either,
    Error,
    Left,
    Null,
    Ok,
    Option,
    ReAwaitable,
    Result,
    Right,
    Some,
    is_error,
    is_left,
    is_null,
    is_ok,
    is_right,
    is_some,
)
from wraps.wraps import (
    WrapOption,
    WrapOptionAwait,
    WrapResult,
    WrapResultAwait,
    wrap_future,
    wrap_future_either,
    wrap_future_option,
    wrap_future_result,
    wrap_option,
    wrap_option_await,
    wrap_option_await_on,
    wrap_option_on,
    wrap_optional,
    wrap_reawaitable,
    wrap_result,
    wrap_result_await,
    wrap_result_await_on,
    wrap_result_on,
)

__all__ = (
    # option
    "Option",
    "Some",
    "Null",
    "NULL",
    "is_some",
    "is_null",
    # result
    "Result",
    "Ok",
    "Error",
    "is_ok",
    "is_error",
    # either
    "Either",
    "Left",
    "Right",
    "is_left",
    "is_right",
    # panics
    "Panic",
    "panic",
    # early decorators
    "early_option",
    "early_option_await",
    "early_result",
    "early_result_await",
    # early errors
    "EarlyOption",
    "EarlyResult",
    # re-awaitable
    "ReAwaitable",
    # future
    "Future",
    # future either
    "FutureEither",
    # future option
    "FutureOption",
    # future result
    "FutureResult",
    # wraps
    "WrapOption",
    "WrapOptionAwait",
    "WrapResult",
    "WrapResultAwait",
    "wrap_option_on",
    "wrap_option_await_on",
    "wrap_option",
    "wrap_option_await",
    "wrap_optional",
    "wrap_result_on",
    "wrap_result_await_on",
    "wrap_result",
    "wrap_result_await",
    "wrap_reawaitable",
    "wrap_future",
    "wrap_future_option",
    "wrap_future_result",
    "wrap_future_either",
)
