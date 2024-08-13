from __future__ import annotations

from typing import Callable, TypeVar

from typing_aliases import Binary, Nullary, Quaternary, Ternary, Unary
from typing_extensions import ParamSpec

from wraps.futures.either import FutureEither
from wraps.futures.future import Future
from wraps.futures.option import FutureOption
from wraps.futures.reawaitable import ReAwaitable
from wraps.futures.result import FutureResult

__all__ = (
    # re-awaitable
    "ReAsyncCallable",
    # futures
    "FutureCallable",
    "FutureNullary",
    "FutureUnary",
    "FutureBinary",
    "FutureTernary",
    "FutureQuaternary",
)

P = ParamSpec("P")

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")

E = TypeVar("E")

L = TypeVar("L")
R = TypeVar("R")


ReAsyncCallable = Callable[P, ReAwaitable[R]]
"""Represents re-awaitable callables `(**P) -> ReAwaitable[R]`."""


FutureCallable = Callable[P, Future[R]]
"""Represents future callables `(**P) -> Future[R]`."""

FutureNullary = Nullary[Future[R]]
"""Represents future nullary functions `() -> Future[R]`."""

FutureUnary = Unary[T, Future[R]]
"""Represents future unary functions `(T) -> Future[R]`."""

FutureBinary = Binary[T, U, Future[R]]
"""Represents future binary functions `(T, U) -> Future[R]`."""

FutureTernary = Ternary[T, U, V, Future[R]]
"""Represents future ternary functions `(T, U, V) -> Future[R]`."""

FutureQuaternary = Quaternary[T, U, V, W, Future[R]]
"""Represents future quaternary functions `(T, U, V, W) -> Future[R]`."""


FutureOptionCallable = Callable[P, FutureOption[T]]
"""Represents future option callables `(**P) -> FutureOption[T]`."""

FutureResultCallable = Callable[P, FutureResult[T, E]]
"""Represents future result callables `(**P) -> FutureResult[T, E]`."""

FutureEitherCallable = Callable[P, FutureEither[L, R]]
"""Represents future either callables `(**P) -> FutureEither[L, R]`."""
