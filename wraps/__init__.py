"""Meaningful and safe wrapping types.

This library implements several types:

- [`Option[T]`][wraps.option.Option] for optional values;
- [`Result[T, E]`][wraps.result.Result] for error handling;
- [`Either[L, R]`][wraps.either.Either] for either values;
- [`Future[T]`][wraps.future.base.Future] for asynchronous abstractions.

The following types are implemented for conveniece:

- [`Future[Option[T]] -> FutureOption[T]`][wraps.future.option.FutureOption];
- [`Future[Result[T, E]] -> FutureResult[T, E]`][wraps.future.result.FutureResult];
- [`Future[Either[L, R]] -> FutureEither[L, R]`][wraps.future.either.FutureEither].

The library also provides various decorators to wrap functions in order to return the types above.
"""

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.9.0"

from wraps.early import early_option, early_option_await, early_result, early_result_await
from wraps.either import Either, Left, Right, is_left, is_right
from wraps.future.base import Future
from wraps.future.either import FutureEither
from wraps.future.option import FutureOption
from wraps.future.result import FutureResult
from wraps.option import NULL, Null, Option, Some, is_null, is_some
from wraps.panics import Panic, panic
from wraps.reawaitable import ReAwaitable, reawaitable
from wraps.result import Error, Ok, Result, is_error, is_ok
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
    wrap_optional,
    wrap_result,
    wrap_result_await,
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
    # panic
    "Panic",
    "panic",
    # early
    "early_option",
    "early_option_await",
    "early_result",
    "early_result_await",
    # re-awaitable
    "ReAwaitable",
    "reawaitable",
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
    "wrap_option",
    "wrap_option_await",
    "wrap_optional",
    "wrap_result",
    "wrap_result_await",
    "wrap_future",
    "wrap_future_option",
    "wrap_future_result",
    "wrap_future_either",
)
