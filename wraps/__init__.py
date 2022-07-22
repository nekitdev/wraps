"""Meaningful and safe wrapping types."""

__description__ = "Meaningful and safe wrapping types."
__url__ = "https://github.com/nekitdev/wraps"

__title__ = "wraps"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.1.0"

from wraps.errors import Panic, panic
from wraps.future import Future, wrap_future
from wraps.future_option import FutureOption, wrap_future_option
from wraps.future_result import FutureResult, wrap_future_result
from wraps.option import (
    Null,
    Option,
    Some,
    convert_optional,
    is_null,
    is_some,
    wrap_option,
    wrap_option_await,
)
from wraps.result import Error, Ok, Result, is_error, is_ok, wrap_result, wrap_result_await
from wraps.shortcuts import option_shortcut, result_shortcut

__all__ = (
    # option
    "Option",
    "Some",
    "Null",
    "is_some",
    "is_null",
    "wrap_option",
    "wrap_option_await",
    # convert
    "convert_optional",
    # result
    "Result",
    "Ok",
    "Error",
    "is_ok",
    "is_error",
    "wrap_result",
    "wrap_result_await",
    # panic
    "Panic",
    "panic",
    # shortcuts
    "option_shortcut",
    "result_shortcut",
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
