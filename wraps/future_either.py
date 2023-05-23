"""Future either values."""

from __future__ import annotations

from typing import Awaitable, TypeVar

from attrs import field, frozen
from typing_extensions import Never, final

from wraps.either import Either, Left, Right
from wraps.future import Future
from wraps.reawaitable import ReAwaitable

__all__ = ("FutureEither",)

L = TypeVar("L", covariant=True)
R = TypeVar("R", covariant=True)

M = TypeVar("M")
S = TypeVar("S")


def reawaitable_converter(awaitable: Awaitable[Either[L, R]]) -> ReAwaitable[Either[L, R]]:
    return ReAwaitable(awaitable)


@final
@frozen()
class FutureEither(Future[Either[L, R]]):
    """[`Future[Either[L, R]]`][wraps.future.Future], adapted to leverage future functionality."""

    reawaitable: ReAwaitable[Either[L, R]] = field(repr=False, converter=reawaitable_converter)

    @classmethod
    def create(cls, awaitable: Awaitable[Either[M, S]]) -> FutureEither[M, S]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_either(cls, either: Either[M, S]) -> FutureEither[M, S]:
        return cls.from_value(either)  # type: ignore

    @classmethod
    def from_left(cls, left: M) -> FutureEither[M, Never]:
        return cls.from_either(Left(left))

    @classmethod
    def from_right(cls, right: S) -> FutureEither[Never, S]:
        return cls.from_either(Right(right))
