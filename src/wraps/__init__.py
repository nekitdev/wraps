"""Meaningful and safe wrapping types."""

from __future__ import annotations

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.15.0"

from wraps import typing
from wraps.early import (
    EarlyOption,
    EarlyResult,
    early_option,
    early_option_await,
    early_result,
    early_result_await,
)
from wraps.either import Either, Left, Right, is_left, is_right
from wraps.futures import (
    Future,
    FutureEither,
    FutureOption,
    FutureResult,
    ReAwaitable,
    future_either,
    future_err,
    future_left,
    future_null,
    future_ok,
    future_option,
    future_result,
    future_right,
    future_some,
    future_value,
    wrap_future,
    wrap_future_either,
    wrap_future_option,
    wrap_future_result,
    wrap_reawaitable,
)
from wraps.markers import UNREACHABLE, unreachable
from wraps.option import (
    NULL,
    Null,
    Option,
    Some,
    WrapOption,
    WrapOptionAwait,
    is_null,
    is_some,
    wrap_option,
    wrap_option_await,
    wrap_option_await_on,
    wrap_option_on,
    wrap_optional,
)
from wraps.panics import PANIC, Panic, panic
from wraps.parse import (
    FromString,
    ParseError,
    SimpleFromString,
    SimpleParseError,
    ToString,
    to_short_string,
    to_string,
)
from wraps.result import (
    Err,
    Ok,
    Result,
    WrapResult,
    WrapResultAwait,
    is_err,
    is_ok,
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
    # optional
    "wrap_optional",
    # option decorators
    "WrapOption",
    "WrapOptionAwait",
    "wrap_option_on",
    "wrap_option_await_on",
    "wrap_option",
    "wrap_option_await",
    # result
    "Result",
    "Ok",
    "Err",
    "is_ok",
    "is_err",
    # result decorators
    "WrapResult",
    "WrapResultAwait",
    "wrap_result_on",
    "wrap_result_await_on",
    "wrap_result",
    "wrap_result_await",
    # either
    "Either",
    "Left",
    "Right",
    "is_left",
    "is_right",
    # early decorators
    "early_option",
    "early_option_await",
    "early_result",
    "early_result_await",
    # early errors
    "EarlyOption",
    "EarlyResult",
    # panics
    "PANIC",
    "Panic",
    "panic",
    # markers
    "UNREACHABLE",
    "unreachable",
    # future
    "Future",
    "future_value",
    "wrap_future",
    # reawaitable
    "ReAwaitable",
    "wrap_reawaitable",
    # future option
    "FutureOption",
    "future_option",
    "future_some",
    "future_null",
    "wrap_future_option",
    # future result
    "FutureResult",
    "future_result",
    "future_ok",
    "future_err",
    "wrap_future_result",
    # future either
    "FutureEither",
    "future_either",
    "future_left",
    "future_right",
    "wrap_future_either",
    # normal
    "FromString",
    "ParseError",
    # simple
    "SimpleFromString",
    "SimpleParseError",
    # format
    "ToString",
    "to_string",
    "to_short_string",
    # typing
    "typing",
)
