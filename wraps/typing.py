from typing import Callable, TypeVar

from typing_aliases import Binary, Nullary, Quaternary, Ternary, Unary
from typing_extensions import ParamSpec

from wraps.future import Future

__all__ = (
    "FutureCallable",
    "FutureNullary",
    "FutureUnary",
    "FutureBinary",
    "FutureTernary",
    "FutureQuaternary",
    "FutureIdentity",
    "FutureInspect",
    "FuturePredicate",
)

P = ParamSpec("P")

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")

R = TypeVar("R")

FutureCallable = Callable[P, Future[R]]
FutureNullary = Nullary[Future[R]]
FutureUnary = Unary[T, Future[R]]
FutureBinary = Binary[T, U, Future[R]]
FutureTernary = Ternary[T, U, V, Future[R]]
FutureQuaternary = Quaternary[T, U, V, W, Future[R]]

FutureIdentity = FutureUnary[T, T]
FutureInspect = FutureUnary[T, None]
FuturePredicate = FutureUnary[T, bool]
