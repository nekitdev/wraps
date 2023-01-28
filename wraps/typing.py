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
"""Represents any exception (error)."""

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")

Nullary = Callable[[], R]
"""Represents nullary functions (`() -> R`)."""
Unary = Callable[[T], R]
"""Represents unary functions (`(T) -> R`)."""
Binary = Callable[[T, U], R]
"""Represents binary functions (`(T, U) -> R`)."""

AsyncNullary = Nullary[Awaitable[R]]
"""Represents async nullary functions (`async () -> R`)."""
AsyncUnary = Unary[T, Awaitable[R]]
"""Represents async unary functions (`async (T) -> R`)."""
AsyncBinary = Binary[T, U, Awaitable[R]]
"""Represents async binary functions (`async (T, U) -> R`)."""

Inspect = Unary[T, None]
"""Represents inspect functions (`(T)`)."""
AsyncInspect = AsyncUnary[T, None]
"""Represents async inspect functions (`async (T)`)."""

Predicate = Unary[T, bool]
"""Represents predicate functions (`(T) -> bool`)."""
AsyncPredicate = AsyncUnary[T, bool]
"""Represents async predicate functions (`async (T) -> bool`)."""
