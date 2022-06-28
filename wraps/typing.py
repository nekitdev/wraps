from typing import Callable, TypeVar

from typing_extensions import TypeAlias

__all__ = ("AnyException", "Nullary", "Unary", "Binary", "Predicate")

AnyException: TypeAlias = BaseException

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")

Nullary = Callable[[], R]
Unary = Callable[[T], R]
Binary = Callable[[T, U], R]

Predicate = Unary[T, bool]
