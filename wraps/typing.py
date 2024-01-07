from typing import Callable, TypeVar

from typing_aliases import AsyncCallable, Binary, Nullary, Quaternary, Ternary, Unary
from typing_extensions import ParamSpec

from wraps.future.base import Future
from wraps.option import Option
from wraps.result import Result

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
E = TypeVar("E")

U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")

R = TypeVar("R")

OptionCallable = Callable[P, Option[T]]
OptionAsyncCallable = AsyncCallable[P, Option[T]]

ResultCallable = Callable[P, Result[T, E]]
ResultAsyncCallable = AsyncCallable[P, Result[T, E]]

FutureCallable = Callable[P, Future[R]]
FutureNullary = Nullary[Future[R]]
FutureUnary = Unary[T, Future[R]]
FutureBinary = Binary[T, U, Future[R]]
FutureTernary = Ternary[T, U, V, Future[R]]
FutureQuaternary = Quaternary[T, U, V, W, Future[R]]

FutureIdentity = FutureUnary[T, T]
FutureInspect = FutureUnary[T, None]
FuturePredicate = FutureUnary[T, bool]
