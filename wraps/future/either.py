"""Future either values."""

from __future__ import annotations

from typing import Awaitable, TypeVar

from attrs import field, frozen
from typing_aliases import (
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)
from typing_extensions import Never, final

from wraps.either import Either, Left, Right
from wraps.future.base import Future
from wraps.reawaitable import ReAwaitable
from wraps.result import Result
from wraps.utils import identity

__all__ = ("FutureEither",)

L = TypeVar("L", covariant=True)
R = TypeVar("R", covariant=True)

M = TypeVar("M")
S = TypeVar("S")

T = TypeVar("T")
U = TypeVar("U")


def reawaitable_converter(awaitable: Awaitable[Either[L, R]]) -> ReAwaitable[Either[L, R]]:
    return ReAwaitable(awaitable)


@final
@frozen()
class FutureEither(Future[Either[L, R]]):
    """[`Future[Either[L, R]]`][wraps.future.base.Future], adapted to leverage future functionality."""

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

    def is_left(self) -> Future[bool]:
        return super().create(self.actual_is_left())

    def is_left_and(self, predicate: Predicate[L]) -> Future[bool]:
        return super().create(self.actual_is_left_and(predicate))

    def is_left_and_await(self, predicate: AsyncPredicate[L]) -> Future[bool]:
        return super().create(self.actual_is_left_and_await(predicate))

    def is_right(self) -> Future[bool]:
        return super().create(self.actual_is_right())

    def is_right_and(self, predicate: Predicate[R]) -> Future[bool]:
        return super().create(self.actual_is_right_and(predicate))

    def is_right_and_await(self, predicate: AsyncPredicate[R]) -> Future[bool]:
        return super().create(self.actual_is_right_and_await(predicate))

    async def actual_is_left(self) -> bool:
        return (await self.reawaitable).is_left()

    async def actual_is_left_and(self, predicate: Predicate[L]) -> bool:
        return (await self.reawaitable).is_left_and(predicate)

    async def actual_is_left_and_await(self, predicate: AsyncPredicate[L]) -> bool:
        return await (await self.reawaitable).is_left_and_await(predicate)

    async def actual_is_right(self) -> bool:
        return (await self.reawaitable).is_right()

    async def actual_is_right_and(self, predicate: Predicate[R]) -> bool:
        return (await self.reawaitable).is_right_and(predicate)

    async def actual_is_right_and_await(self, predicate: AsyncPredicate[R]) -> bool:
        return await (await self.reawaitable).is_right_and_await(predicate)

    def expect_left(self, message: str) -> Future[L]:
        return super().create(self.actual_expect_left(message))

    def expect_right(self, message: str) -> Future[R]:
        return super().create(self.actual_expect_right(message))

    async def actual_expect_left(self, message: str) -> L:
        return (await self.awaitable).expect_left(message)

    async def actual_expect_right(self, message: str) -> R:
        return (await self.awaitable).expect_right(message)

    def unwrap_left(self) -> Future[L]:
        return super().create(self.actual_unwrap_left())

    def unwrap_right(self) -> Future[R]:
        return super().create(self.actual_unwrap_right())

    async def actual_unwrap_left(self) -> L:
        return (await self.awaitable).unwrap_left()

    async def actual_unwrap_right(self) -> R:
        return (await self.awaitable).unwrap_right()

    def left(self) -> FutureOption[L]:
        return FutureOption(self.actual_left())

    def left_or(self, default: L) -> Future[L]:  # type: ignore
        return super().create(self.actual_left_or(default))

    def left_or_else(self, default: Nullary[L]) -> Future[L]:
        return super().create(self.actual_left_or_else(default))

    def left_or_else_await(self, default: AsyncNullary[L]) -> Future[L]:
        return super().create(self.actual_left_or_else_await(default))

    async def actual_left(self) -> Option[L]:
        return (await self.awaitable).left()

    async def actual_left_or(self, default: L) -> L:  # type: ignore
        return (await self.awaitable).left_or(default)

    async def actual_left_or_else(self, default: Nullary[L]) -> L:
        return (await self.awaitable).left_or_else(default)

    async def actual_left_or_else_await(self, default: AsyncNullary[L]) -> L:
        return await (await self.awaitable).left_or_else_await(default)

    def right(self) -> FutureOption[R]:
        return FutureOption(self.actual_right())

    def right_or(self, default: R) -> Future[R]:  # type: ignore
        return super().create(self.actual_right_or(default))

    def right_or_else(self, default: Nullary[R]) -> Future[R]:
        return super().create(self.actual_right_or_else(default))

    def right_or_else_await(self, default: AsyncNullary[R]) -> Future[R]:
        return super().create(self.actual_right_or_else_await(default))

    async def actual_right(self) -> Option[R]:
        return (await self.awaitable).right()

    async def actual_right_or(self, default: R) -> R:  # type: ignore
        return (await self.awaitable).right_or(default)

    async def actual_right_or_else(self, default: Nullary[R]) -> R:
        return (await self.awaitable).right_or_else(default)

    async def actual_right_or_else_await(self, default: AsyncNullary[R]) -> R:
        return await (await self.awaitable).right_or_else_await(default)

    def into_either(self: FutureEither[T, T]) -> Future[T]:
        return super().create(self.actual_into_either())

    async def actual_into_either(self: FutureEither[T, T]) -> T:
        return (await self.awaitable).into_either()

    def inspect_left(self, inspect: Inspect[L]) -> FutureEither[L, R]:
        return self.create(self.actual_inspect_left(inspect))

    def inspect_left_await(self, inspect: AsyncInspect[L]) -> FutureEither[L, R]:
        return self.create(self.actual_inspect_left_await(inspect))

    def inspect_right(self, inspect: Inspect[R]) -> FutureEither[L, R]:
        return self.create(self.actual_inspect_right(inspect))

    def inspect_right_await(self, inspect: AsyncInspect[R]) -> FutureEither[L, R]:
        return self.create(self.actual_inspect_right_await(inspect))

    async def actual_inspect_left(self, inspect: Inspect[L]) -> Either[L, R]:
        return (await self.awaitable).inspect_left(inspect)

    async def actual_inspect_left_await(self, inspect: AsyncInspect[L]) -> Either[L, R]:
        return await (await self.awaitable).inspect_left_await(inspect)

    async def actual_inspect_right(self, inspect: Inspect[R]) -> Either[L, R]:
        return (await self.awaitable).inspect_right(inspect)

    async def actual_inspect_right_await(self, inspect: AsyncInspect[R]) -> Either[L, R]:
        return await (await self.awaitable).inspect_right_await(inspect)

    async def flip(self) -> FutureEither[R, L]:
        return self.create(self.actual_flip())

    async def actual_flip(self) -> Either[R, L]:
        return (await self.awaitable).flip()

    def map_left(self, function: Unary[L, M]) -> FutureEither[M, R]:
        return self.create(self.actual_map_left(function))

    def map_left_await(self, function: AsyncUnary[L, M]) -> FutureEither[M, R]:
        return self.create(self.actual_map_left_await(function))

    def map_right(self, function: Unary[R, S]) -> FutureEither[L, S]:
        return self.create(self.actual_map_right(function))

    def map_right_await(self, function: AsyncUnary[R, S]) -> FutureEither[L, S]:
        return self.create(self.actual_map_right_await(function))

    async def actual_map_left(self, function: Unary[L, M]) -> Either[M, R]:
        return (await self.awaitable).map_left(function)

    async def actual_map_left_await(self, function: AsyncUnary[L, M]) -> Either[M, R]:
        return await (await self.awaitable).map_left_await(function)

    async def actual_map_right(self, function: Unary[R, S]) -> Either[L, S]:
        return (await self.awaitable).map_right(function)

    async def actual_map_right_await(self, function: AsyncUnary[R, S]) -> Either[L, S]:
        return await (await self.awaitable).map_right_await(function)

    def map(self: FutureEither[T, T], function: Unary[T, U]) -> FutureEither[U, U]:
        return self.create(self.actual_map(function))

    def map_await(self: FutureEither[T, T], function: AsyncUnary[T, U]) -> FutureEither[U, U]:
        return self.create(self.actual_map_await(function))

    async def actual_map(self: FutureEither[T, T], function: Unary[T, U]) -> Either[U, U]:
        return (await self.awaitable).map(function)

    async def actual_map_await(
        self: FutureEither[T, T], function: AsyncUnary[T, U]
    ) -> Either[U, U]:
        return await (await self.awaitable).map_await(function)

    def map_either(self, left: Unary[L, M], right: Unary[R, S]) -> FutureEither[M, S]:
        return self.create(self.actual_map_either(left, right))

    def map_either_await(
        self, left: AsyncUnary[L, M], right: AsyncUnary[R, S]
    ) -> FutureEither[M, S]:
        return self.create(self.actual_map_either_await(left, right))

    async def actual_map_either(self, left: Unary[L, M], right: Unary[R, S]) -> Either[M, S]:
        return (await self.awaitable).map_either(left, right)

    async def actual_map_either_await(
        self, left: AsyncUnary[L, M], right: AsyncUnary[R, S]
    ) -> Either[M, S]:
        return await (await self.awaitable).map_either_await(left, right)

    def either(self, left: Unary[L, T], right: Unary[R, T]) -> Future[T]:
        return super().create(self.actual_either(left, right))

    def either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> Future[T]:
        return super().create(self.actual_either_await(left, right))

    async def actual_either(self, left: Unary[L, T], right: Unary[R, T]) -> T:
        return (await self.awaitable).either(left, right)

    async def actual_either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> T:
        return await (await self.awaitable).either_await(left, right)

    def left_and_then(self, function: Unary[L, Either[M, R]]) -> FutureEither[M, R]:
        return self.create(self.actual_left_and_then(function))

    def left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> FutureEither[M, R]:
        return self.create(self.actual_left_and_then_await(function))

    def right_and_then(self, function: Unary[R, Either[L, S]]) -> FutureEither[L, S]:
        return self.create(self.actual_right_and_then(function))

    def right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> FutureEither[L, S]:
        return self.create(self.actual_right_and_then_await(function))

    async def actual_left_and_then(self, function: Unary[L, Either[M, R]]) -> Either[M, R]:
        return (await self.awaitable).left_and_then(function)

    async def actual_left_and_then_await(
        self, function: AsyncUnary[L, Either[M, R]]
    ) -> Either[M, R]:
        return await (await self.awaitable).left_and_then_await(function)

    async def actual_right_and_then(self, function: Unary[R, Either[L, S]]) -> Either[L, S]:
        return (await self.awaitable).right_and_then(function)

    async def actual_right_and_then_await(
        self, function: AsyncUnary[R, Either[L, S]]
    ) -> Either[L, S]:
        return await (await self.awaitable).right_and_then_await(function)

    def flatten_left(self: FutureEither[FutureEither[L, R], R]) -> FutureEither[L, R]:
        return self.left_and_then(identity)  # type: ignore

    def flatten_right(self: FutureEither[L, FutureEither[L, R]]) -> FutureEither[L, R]:
        return self.right_and_then(identity)  # type: ignore

    def contains_left(self, value: M) -> Future[bool]:
        return super().create(self.actual_contains_left(value))

    def contains_right(self, value: S) -> Future[bool]:
        return super().create(self.actual_contains_right(value))

    async def actual_contains_left(self, value: M) -> bool:
        return (await self.reawaitable).contains_left(value)

    async def actual_contains_right(self, value: S) -> bool:
        return (await self.reawaitable).contains_right(value)

    def contains(self: FutureEither[T, T], value: U) -> Future[bool]:
        return super().create(self.actual_contains(value))

    async def actual_contains(self: FutureEither[T, T], value: U) -> bool:
        return (await self.reawaitable).contains(value)

    def into_result(self) -> FutureResult[L, R]:
        return FutureResult(self.actual_into_result())

    async def actual_into_result(self) -> Result[L, R]:
        return (await self.awaitable).into_result()


from wraps.future.option import FutureOption
from wraps.future.result import FutureResult
from wraps.option import Option
