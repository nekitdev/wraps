from typing import Awaitable, Callable, TypeVar

from typing_extensions import TypeAlias

__all__ = (
    "AnyException",
    "Nullary",
    "Unary",
    "Binary",
    "AsyncNullary",
    "AsyncUnary",
    "AsyncBinary",
    "Inspect",
    "AsyncInspect",
    "Predicate",
    "AsyncPredicate",
)

AnyException: TypeAlias = BaseException

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")

Nullary = Callable[[], R]
Unary = Callable[[T], R]
Binary = Callable[[T, U], R]

AsyncNullary = Nullary[Awaitable[R]]
AsyncUnary = Unary[T, Awaitable[R]]
AsyncBinary = Binary[T, U, Awaitable[R]]

Inspect = Unary[T, None]
AsyncInspect = AsyncUnary[T, None]

Predicate = Unary[T, bool]
AsyncPredicate = AsyncUnary[T, bool]
