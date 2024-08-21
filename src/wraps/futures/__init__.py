from __future__ import annotations

from wraps.futures import typing
from wraps.futures.either import (
    FutureEither,
    future_either,
    future_left,
    future_right,
    wrap_future_either,
)
from wraps.futures.future import Future, future_value, wrap_future
from wraps.futures.option import (
    FutureOption,
    future_null,
    future_option,
    future_some,
    wrap_future_option,
)
from wraps.futures.reawaitable import ReAwaitable, wrap_reawaitable
from wraps.futures.result import (
    FutureResult,
    future_err,
    future_ok,
    future_result,
    wrap_future_result,
)

__all__ = (
    # future
    "Future",
    "future_value",
    "wrap_future",
    # reawaitable
    "ReAwaitable",
    "wrap_reawaitable",
    # option
    "FutureOption",
    "future_option",
    "future_some",
    "future_null",
    "wrap_future_option",
    # result
    "FutureResult",
    "future_result",
    "future_ok",
    "future_err",
    "wrap_future_result",
    # either
    "FutureEither",
    "future_either",
    "future_left",
    "future_right",
    "wrap_future_either",
    # typing
    "typing",
)
