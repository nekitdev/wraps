from typing import Callable, TypeVar

from typing_aliases import Binary, Nullary, Quaternary, Ternary, Unary
from typing_extensions import ParamSpec

from wraps.futures.base import Future

__all__ = (
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

R = TypeVar("R")


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
