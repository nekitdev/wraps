"""Meaningful and safe wrapping types."""

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.3.0"

from wraps.early import early_option, early_option_await, early_result, early_result_await
from wraps.either import Either, Left, Right, is_left, is_right
from wraps.errors import Panic, panic
from wraps.future import Future
from wraps.future_option import FutureOption
from wraps.future_result import FutureResult
from wraps.option import Null, Option, Some, is_null, is_some
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
    wrap_result,
    wrap_result_await,
)

__all__ = (
    # option
    "Option",
    "Some",
    "Null",
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
    "wrap_result",
    "wrap_result_await",
    "wrap_future",
    "wrap_future_option",
    "wrap_future_result",
    "wrap_future_either",
)
