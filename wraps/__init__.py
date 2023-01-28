"""Meaningful and safe wrapping types."""

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.3.0"

from wraps.early import early_option, early_result
from wraps.either import Either, Left, Right, is_left, is_right
from wraps.errors import Panic, panic
from wraps.future import Future, wrap_future
from wraps.future_option import FutureOption, wrap_future_option
from wraps.future_result import FutureResult, wrap_future_result
from wraps.option import (
    Null,
    Option,
    Some,
    is_null,
    is_some,
    wrap_option,
    wrap_option_await,
    wrap_optional,
)
from wraps.result import Error, Ok, Result, is_error, is_ok, wrap_result, wrap_result_await

__all__ = (
    # option
    "Option",
    "Some",
    "Null",
    "is_some",
    "is_null",
    "wrap_option",
    "wrap_option_await",
    # optional
    "wrap_optional",
    # result
    "Result",
    "Ok",
    "Error",
    "is_ok",
    "is_error",
    "wrap_result",
    "wrap_result_await",
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
    "early_result",
    # future
    "Future",
    "wrap_future",
    # future option
    "FutureOption",
    "wrap_future_option",
    # future result
    "FutureResult",
    "wrap_future_result",
)
