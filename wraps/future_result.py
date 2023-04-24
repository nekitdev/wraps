from __future__ import annotations

from typing import Awaitable, TypeVar, final

from attrs import frozen
from funcs.typing import AsyncInspect, AsyncNullary, AsyncUnary, Inspect, Nullary, Unary
from typing_extensions import Never

from wraps.future import Future
from wraps.option import Option
from wraps.reawaitable import ReAwaitable
from wraps.result import Error, Ok, Result, is_error, is_ok
from wraps.utils import identity

__all__ = ("FutureResult",)

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")


V = TypeVar("V")


@final
@frozen()
class FutureResult(Future[Result[T, E]]):
    """[`Future[Result[T, E]]`][wraps.future.Future], adapted to leverage future functionality."""

    @classmethod
    def from_awaitable(cls, awaitable: Awaitable[Result[U, F]]) -> FutureResult[U, F]:  # type: ignore
        return cls(ReAwaitable(awaitable))  # type: ignore

    @classmethod
    def from_result(cls, result: Result[U, F]) -> FutureResult[U, F]:
        return cls.from_value(result)  # type: ignore

    @classmethod
    def from_ok(cls, value: U) -> FutureResult[U, Never]:
        return cls.from_result(Ok(value))

    @classmethod
    def from_error(cls, value: F) -> FutureResult[Never, F]:
        return cls.from_result(Error(value))

    def expect(self, message: str) -> Future[T]:
        return super().from_awaitable(self.actual_expect(message))

    def expect_error(self, message: str) -> Future[E]:
        return super().from_awaitable(self.actual_expect_error(message))

    async def actual_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

    async def actual_expect_error(self, message: str) -> E:
        return (await self.awaitable).expect_error(message)

    def unwrap(self) -> Future[T]:
        return super().from_awaitable(self.actual_unwrap())

    def unwrap_or(self, default: T) -> Future[T]:  # type: ignore
        return super().from_awaitable(self.actual_unwrap_or(default))

    def unwrap_or_else(self, default: Nullary[T]) -> Future[T]:
        return super().from_awaitable(self.actual_unwrap_or_else(default))

    def unwrap_or_else_await(self, default: AsyncNullary[T]) -> Future[T]:
        return super().from_awaitable(self.actual_unwrap_or_else_await(default))

    async def actual_unwrap(self) -> T:
        return (await self.awaitable).unwrap()

    async def actual_unwrap_or(self, default: T) -> T:  # type: ignore
        return (await self.awaitable).unwrap_or(default)

    async def actual_unwrap_or_else(self, default: Nullary[T]) -> T:
        return (await self.awaitable).unwrap_or_else(default)

    async def actual_unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        return await (await self.awaitable).unwrap_or_else_await(default)

    def unwrap_error(self) -> Future[E]:
        return super().from_awaitable(self.actual_unwrap_error())

    def unwrap_error_or(self, default: E) -> Future[E]:  # type: ignore
        return super().from_awaitable(self.actual_unwrap_error_or(default))

    def unwrap_error_or_else(self, default: Nullary[E]) -> Future[E]:
        return super().from_awaitable(self.actual_unwrap_error_or_else(default))

    def unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> Future[E]:
        return super().from_awaitable(self.actual_unwrap_error_or_else_await(default))

    async def actual_unwrap_error(self) -> E:
        return (await self.awaitable).unwrap_error()

    async def actual_unwrap_error_or(self, default: E) -> E:  # type: ignore
        return (await self.awaitable).unwrap_error_or(default)

    async def actual_unwrap_error_or_else(self, default: Nullary[E]) -> E:
        return (await self.awaitable).unwrap_error_or_else(default)

    async def actual_unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> E:
        return await (await self.awaitable).unwrap_error_or_else_await(default)

    def ok(self) -> FutureOption[T]:
        return FutureOption.from_awaitable(self.actual_ok())

    def error(self) -> FutureOption[E]:
        return FutureOption.from_awaitable(self.actual_error())

    async def actual_ok(self) -> Option[T]:
        return (await self.awaitable).ok()

    async def actual_error(self) -> Option[E]:
        return (await self.awaitable).error()

    def inspect(self, function: Inspect[T]) -> FutureResult[T, E]:
        return self.from_awaitable(self.actual_inspect(function))

    def inspect_error(self, function: Inspect[E]) -> FutureResult[T, E]:
        return self.from_awaitable(self.actual_inspect_error(function))

    def inspect_await(self, function: AsyncInspect[T]) -> FutureResult[T, E]:
        return self.from_awaitable(self.actual_inspect_await(function))

    def inspect_error_await(self, function: AsyncInspect[E]) -> FutureResult[T, E]:
        return self.from_awaitable(self.actual_inspect_error_await(function))

    async def actual_inspect(self, function: Inspect[T]) -> Result[T, E]:
        return (await self.awaitable).inspect(function)

    async def actual_inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        return (await self.awaitable).inspect_error(function)

    async def actual_inspect_await(self, function: AsyncInspect[T]) -> Result[T, E]:
        return await (await self.awaitable).inspect_await(function)

    async def actual_inspect_error_await(self, function: AsyncInspect[E]) -> Result[T, E]:
        return await (await self.awaitable).inspect_error_await(function)

    def map(self, function: Unary[T, U]) -> FutureResult[U, E]:
        return self.from_awaitable(self.actual_map(function))

    def map_or(self, default: U, function: Unary[T, U]) -> Future[U]:
        return super().from_awaitable(self.actual_map_or(default, function))

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> Future[U]:
        return super().from_awaitable(self.actual_map_or_else(default, function))

    def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> Future[U]:
        return super().from_awaitable(self.actual_map_or_else_await(default, function))

    def map_error(self, function: Unary[E, F]) -> FutureResult[T, F]:
        return self.from_awaitable(self.actual_map_error(function))

    def map_error_or(self, default: F, function: Unary[E, F]) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_or(default, function))

    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_or_else(default, function))

    def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_or_else_await(default, function))

    async def actual_map(self, function: Unary[T, U]) -> Result[U, E]:
        return (await self.awaitable).map(function)

    async def actual_map_or(self, default: U, function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or(default, function)

    async def actual_map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or_else(default, function)

    async def actual_map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await (await self.awaitable).map_or_else_await(default, function)

    async def actual_map_error(self, function: Unary[E, F]) -> Result[T, F]:
        return (await self.awaitable).map_error(function)

    async def actual_map_error_or(self, default: F, function: Unary[E, F]) -> F:
        return (await self.awaitable).map_error_or(default, function)

    async def actual_map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return (await self.awaitable).map_error_or_else(default, function)

    async def actual_map_error_or_else_await(
        self, default: AsyncNullary[F], function: Unary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_or_else_await(default, function)

    def map_await(self, function: AsyncUnary[T, U]) -> FutureResult[U, E]:
        return self.from_awaitable(self.actual_map_await(function))

    def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> Future[U]:
        return super().from_awaitable(self.actual_map_await_or(default, function))

    def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> Future[U]:
        return super().from_awaitable(self.actual_map_await_or_else(default, function))

    def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> Future[U]:
        return super().from_awaitable(self.actual_map_await_or_else_await(default, function))

    def map_error_await(self, function: AsyncUnary[E, F]) -> FutureResult[T, F]:
        return self.from_awaitable(self.actual_map_error_await(function))

    def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_await_or(default, function))

    def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_await_or_else(default, function))

    def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> Future[F]:
        return super().from_awaitable(self.actual_map_error_await_or_else_await(default, function))

    async def actual_map_await(self, function: AsyncUnary[T, U]) -> Result[U, E]:
        return await (await self.awaitable).map_await(function)

    async def actual_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def actual_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def actual_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    async def actual_map_error_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        return await (await self.awaitable).map_error_await(function)

    async def actual_map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return await (await self.awaitable).map_error_await_or(default, function)

    async def actual_map_error_await_or_else(
        self, default: Nullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_await_or_else(default, function)

    async def actual_map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_await_or_else_await(default, function)

    def and_then(self, function: Unary[T, Result[U, E]]) -> FutureResult[U, E]:
        return self.from_awaitable(self.actual_and_then(function))

    def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> FutureResult[U, E]:
        return self.from_awaitable(self.actual_and_then_await(function))

    def or_else(self, function: Unary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.from_awaitable(self.actual_or_else(function))

    def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.from_awaitable(self.actual_or_else_await(function))

    async def actual_and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return (await self.awaitable).and_then(function)

    async def actual_and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        return await (await self.awaitable).and_then_await(function)

    async def actual_or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return (await self.awaitable).or_else(function)

    async def actual_or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await (await self.awaitable).or_else_await(function)

    def and_then_future(self, function: Unary[T, FutureResult[U, E]]) -> FutureResult[U, E]:
        return self.from_awaitable(self.actual_and_then_future(function))

    def or_else_future(self, function: Unary[E, FutureResult[T, F]]) -> FutureResult[T, F]:
        return self.from_awaitable(self.actual_or_else_future(function))

    async def actual_and_then_future(self, function: Unary[T, FutureResult[U, E]]) -> Result[U, E]:
        result = await self.awaitable

        if is_ok(result):
            return await function(result.unwrap())

        return result  # type: ignore  # guaranteed `Error[E]`

    async def actual_or_else_future(self, function: Unary[E, FutureResult[T, F]]) -> Result[T, F]:
        result = await self.awaitable

        if is_error(result):
            return await function(result.unwrap_error())

        return result  # type: ignore  # guaranteed `Ok[T]`

    def try_flatten(self: FutureResult[FutureResult[T, E], E]) -> FutureResult[T, E]:
        return self.and_then_future(identity)

    def try_flatten_error(self: FutureResult[T, FutureResult[T, E]]) -> FutureResult[T, E]:
        return self.or_else_future(identity)

    def flip(self) -> FutureResult[E, T]:
        return self.from_awaitable(self.actual_flip())

    async def actual_flip(self) -> Result[E, T]:
        return (await self.awaitable).flip()

    def into_ok_or_error(self: FutureResult[T, T]) -> Future[T]:
        return super().from_awaitable(self.actual_into_ok_or_error())

    async def actual_into_ok_or_error(self: FutureResult[T, T]) -> T:
        return (await self.awaitable).into_ok_or_error()

    def into_future(self) -> Future[Result[T, E]]:
        return super().from_awaitable(self.awaitable)


from wraps.future_option import FutureOption
