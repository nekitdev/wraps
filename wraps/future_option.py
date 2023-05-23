"""Future optional values."""

from __future__ import annotations

from typing import Awaitable, Optional, Tuple, TypeVar

from attrs import field, frozen
from typing_aliases import (
    AsyncBinary,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Binary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)
from typing_extensions import Never, final

from wraps.future import Future, identity
from wraps.option import Null, Option, Some
from wraps.reawaitable import ReAwaitable
from wraps.result import Result

__all__ = ("FutureOption",)

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E", covariant=True)
F = TypeVar("F")


def reawaitable_converter(awaitable: Awaitable[Option[T]]) -> ReAwaitable[Option[T]]:
    return ReAwaitable(awaitable)


@final
@frozen()
class FutureOption(Future[Option[T]]):
    """[`Future[Option[T]]`][wraps.future.Future], adapted to leverage future functionality."""

    reawaitable: ReAwaitable[Option[T]] = field(repr=False, converter=reawaitable_converter)

    @classmethod
    def create(cls, awaitable: Awaitable[Option[U]]) -> FutureOption[U]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_option(cls, option: Option[U]) -> FutureOption[U]:
        return cls.from_value(option)  # type: ignore

    @classmethod
    def from_some(cls, value: U) -> FutureOption[U]:
        return cls.from_option(Some(value))

    @classmethod
    def from_null(cls) -> FutureOption[Never]:
        return cls.from_option(Null())

    def is_some(self) -> Future[bool]:
        return super().create(self.actual_is_some())

    def is_some_and(self, predicate: Predicate[T]) -> Future[bool]:
        return super().create(self.actual_is_some_and(predicate))

    def is_some_and_await(self, predicate: AsyncPredicate[T]) -> Future[bool]:
        return super().create(self.actual_is_some_and_await(predicate))

    def is_null(self) -> Future[bool]:
        return super().create(self.actual_is_null())

    async def actual_is_some(self) -> bool:
        return (await self.awaitable).is_some()

    async def actual_is_some_and(self, predicate: Predicate[T]) -> bool:
        return (await self.awaitable).is_some_and(predicate)

    async def actual_is_some_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await (await self.awaitable).is_some_and_await(predicate)

    async def actual_is_null(self) -> bool:
        return (await self.awaitable).is_null()

    def expect(self, message: str) -> Future[T]:
        return super().create(self.actual_expect(message))

    async def actual_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

    def extract(self) -> Future[Optional[T]]:
        return super().create(self.actual_extract())

    async def actual_extract(self) -> Optional[T]:
        return (await self.awaitable).extract()

    def unwrap(self) -> Future[T]:
        return super().create(self.actual_unwrap())

    def unwrap_or(self, default: T) -> Future[T]:  # type: ignore
        return super().create(self.actual_unwrap_or(default))

    def unwrap_or_else(self, default: Nullary[T]) -> Future[T]:
        return super().create(self.actual_unwrap_or_else(default))

    def unwrap_or_else_await(self, default: AsyncNullary[T]) -> Future[T]:
        return super().create(self.actual_unwrap_or_else_await(default))

    async def actual_unwrap(self) -> T:
        return (await self.awaitable).unwrap()

    async def actual_unwrap_or(self, default: T) -> T:  # type: ignore
        return (await self.awaitable).unwrap_or(default)

    async def actual_unwrap_or_else(self, default: Nullary[T]) -> T:
        return (await self.awaitable).unwrap_or_else(default)

    async def actual_unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        return await (await self.awaitable).unwrap_or_else_await(default)

    def inspect(self, function: Inspect[T]) -> FutureOption[T]:
        return self.create(self.actual_inspect(function))

    def inspect_await(self, function: AsyncInspect[T]) -> FutureOption[T]:
        return self.create(self.actual_inspect_await(function))

    async def actual_inspect(self, function: Inspect[T]) -> Option[T]:
        return (await self.awaitable).inspect(function)

    async def actual_inspect_await(self, function: AsyncInspect[T]) -> Option[T]:
        return await (await self.awaitable).inspect_await(function)

    def map(self, function: Unary[T, U]) -> FutureOption[U]:
        return self.create(self.actual_map(function))

    def map_or(self, default: U, function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or(default, function))

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or_else(default, function))

    def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or_else_await(default, function))

    def map_await(self, function: AsyncUnary[T, U]) -> FutureOption[U]:
        return self.create(self.actual_map_await(function))

    def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.actual_map_await_or(default, function))

    def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.actual_map_await_or_else(default, function))

    def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> Future[U]:
        return super().create(self.actual_map_await_or_else_await(default, function))

    async def actual_map(self, function: Unary[T, U]) -> Option[U]:
        return (await self.awaitable).map(function)

    async def actual_map_or(self, default: U, function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or(default, function)

    async def actual_map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or_else(default, function)

    async def actual_map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await (await self.awaitable).map_or_else_await(default, function)

    async def actual_map_await(self, function: AsyncUnary[T, U]) -> Option[U]:
        return await (await self.awaitable).map_await(function)

    async def actual_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def actual_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def actual_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    def ok_or(self, error: F) -> FutureResult[T, F]:
        return FutureResult(self.actual_ok_or(error))

    def ok_or_else(self, error: Nullary[E]) -> FutureResult[T, E]:
        return FutureResult(self.actual_ok_or_else(error))

    def ok_or_else_await(self, error: AsyncNullary[E]) -> FutureResult[T, E]:
        return FutureResult(self.actual_ok_or_else_await(error))

    async def actual_ok_or(self, error: E) -> Result[T, E]:  # type: ignore
        return (await self.awaitable).ok_or(error)

    async def actual_ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        return (await self.awaitable).ok_or_else(error)

    async def actual_ok_or_else_await(self, error: AsyncNullary[E]) -> Result[T, E]:
        return await (await self.awaitable).ok_or_else_await(error)

    def and_then(self, function: Unary[T, Option[U]]) -> FutureOption[U]:
        return self.create(self.actual_and_then(function))

    def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> FutureOption[U]:
        return self.create(self.actual_and_then_await(function))

    def or_else(self, function: Nullary[Option[T]]) -> FutureOption[T]:
        return self.create(self.actual_or_else(function))

    def or_else_await(self, function: AsyncNullary[Option[T]]) -> FutureOption[T]:
        return self.create(self.actual_or_else_await(function))

    async def actual_and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        return (await self.awaitable).and_then(function)

    async def actual_and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Option[U]:
        return await (await self.awaitable).and_then_await(function)

    async def actual_or_else(self, function: Nullary[Option[T]]) -> Option[T]:
        return (await self.awaitable).or_else(function)

    async def actual_or_else_await(self, function: AsyncNullary[Option[T]]) -> Option[T]:
        return await (await self.awaitable).or_else_await(function)

    def filter(self, predicate: Predicate[T]) -> FutureOption[T]:
        return self.create(self.actual_filter(predicate))

    def filter_await(self, predicate: AsyncPredicate[T]) -> FutureOption[T]:
        return self.create(self.actual_filter_await(predicate))

    async def actual_filter(self, predicate: Predicate[T]) -> Option[T]:
        return (await self.awaitable).filter(predicate)

    async def actual_filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        return await (await self.awaitable).filter_await(predicate)

    def xor(self, option: FutureOption[T]) -> FutureOption[T]:
        return self.create(self.actual_xor(option))

    async def actual_xor(self, option: FutureOption[T]) -> Option[T]:
        return (await self.awaitable).xor(await option.awaitable)

    def zip(self, option: FutureOption[U]) -> FutureOption[Tuple[T, U]]:
        return self.create(self.actual_zip(option))

    def zip_with(self, option: FutureOption[U], function: Binary[T, U, V]) -> FutureOption[V]:
        return self.create(self.actual_zip_with(option, function))

    def zip_with_await(
        self, option: FutureOption[U], function: AsyncBinary[T, U, V]
    ) -> FutureOption[V]:
        return self.create(self.actual_zip_with_await(option, function))

    async def actual_zip(self, option: FutureOption[U]) -> Option[Tuple[T, U]]:
        return (await self.awaitable).zip(await option.awaitable)

    async def actual_zip_with(
        self, option: FutureOption[U], function: Binary[T, U, V]
    ) -> Option[V]:
        return (await self.awaitable).zip_with(await option.awaitable, function)

    async def actual_zip_with_await(
        self, option: FutureOption[U], function: AsyncBinary[T, U, V]
    ) -> Option[V]:
        return await (await self.awaitable).zip_with_await(await option.awaitable, function)

    def unzip(self: FutureOption[Tuple[U, V]]) -> Tuple[FutureOption[U], FutureOption[V]]:
        async def unzipper() -> Tuple[Option[U], Option[V]]:
            return (await self.awaitable).unzip()

        async def former() -> Option[U]:
            u, _ = await unzipper()

            return u

        async def latter() -> Option[V]:
            _, v = await unzipper()

            return v

        return (self.create(former()), self.create(latter()))

    def flatten(self: FutureOption[FutureOption[U]]) -> FutureOption[U]:
        return self.create(self.actual_flatten())

    async def actual_flatten(self: FutureOption[FutureOption[U]]) -> Option[U]:
        return await self.and_then_await(identity)

    def contains(self, value: U) -> Future[bool]:
        return super().create(self.actual_contains(value))

    async def actual_contains(self, value: U) -> bool:
        return (await self.awaitable).contains(value)

    def early(self) -> Future[T]:
        return super().create(self.actual_early())

    async def actual_early(self) -> T:
        return (await self.awaitable).early()


from wraps.future_result import FutureResult
