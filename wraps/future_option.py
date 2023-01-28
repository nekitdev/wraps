from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from attrs import field, frozen
from typing_extensions import Never, ParamSpec

from wraps.future import Future, ReAwaitable, identity
from wraps.option import Null, Option, Some, is_null, is_some
from wraps.result import Result
from wraps.typing import (
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)

__all__ = ("FutureOption", "wrap_future_option")

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")


@frozen()
class FutureOption(Future[Option[T]]):
    """[`Future[Option[T]]`][wraps.future.Future], adapted to leverage future functionality."""

    awaitable: ReAwaitable[Option[T]] = field(repr=False, converter=ReAwaitable)

    @classmethod
    def create(cls, awaitable: Awaitable[Option[U]]) -> FutureOption[U]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_some(cls, value: U) -> FutureOption[U]:
        return cls.from_value(Some(value))  # type: ignore

    @classmethod
    def from_null(cls) -> FutureOption[Never]:
        return cls.from_value(Null())  # type: ignore

    def expect(self, message: str) -> Future[T]:
        return super().create(self.actual_expect(message))

    async def actual_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

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
        return await (await self.awaitable).inspect_await(function)  # type: ignore

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
        return await (await self.awaitable).map_await(function)  # type: ignore

    async def actual_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def actual_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def actual_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    def ok_or(self, error: F) -> FutureResult[T, F]:
        return FutureResult.create(self.actual_ok_or(error))

    def ok_or_else(self, error: Nullary[E]) -> FutureResult[T, E]:
        return FutureResult.create(self.actual_ok_or_else(error))

    def ok_or_else_await(self, error: AsyncNullary[E]) -> FutureResult[T, E]:
        return FutureResult.create(self.actual_ok_or_else_await(error))

    async def actual_ok_or(self, error: E) -> Result[T, E]:  # type: ignore
        return (await self.awaitable).ok_or(error)

    async def actual_ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        return (await self.awaitable).ok_or_else(error)

    async def actual_ok_or_else_await(self, error: AsyncNullary[E]) -> Result[T, E]:
        return await (await self.awaitable).ok_or_else_await(error)  # type: ignore

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

    def and_then_future(self, function: Unary[T, FutureOption[U]]) -> FutureOption[U]:
        return self.create(self.actual_and_then_future(function))

    def or_else_future(self, function: Nullary[FutureOption[T]]) -> FutureOption[T]:
        return self.create(self.actual_or_else_future(function))

    async def actual_and_then_future(self, function: Unary[T, FutureOption[U]]) -> Option[U]:
        option = await self.awaitable

        if is_some(option):
            return await function(option.unwrap())

        return option  # type: ignore  # guaranteed `Null`

    async def actual_or_else_future(self, function: Nullary[FutureOption[T]]) -> Option[T]:
        option = await self.awaitable

        if is_null(option):
            return await function()

        return option

    def flatten(self: FutureOption[FutureOption[U]]) -> FutureOption[U]:
        return self.and_then_future(identity)


P = ParamSpec("P")


def wrap_future_option(function: Callable[P, Awaitable[T]]) -> Callable[P, FutureOption[T]]:
    """Wraps an asynchronous `function` returning `T` into a function
    returning [`FutureOption[T]`][wraps.future_option.FutureOption].

    This handles all exceptions via returning [`Null`][wraps.option.Null] on errors,
    wrapping the resulting `value` into [`Some(value)`][wraps.option.Some].

    Example:
        ```python
        @wrap_future_option
        async def identity(value: T) -> T:
            return value

        value = 42

        assert await identity(value).unwrap() == value
        ```

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The wrapping function.
    """

    async def wrapping(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(await function(*args, **kwargs))

        except Exception:
            return Null()

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureOption[T]:
        return FutureOption(wrapping(*args, **kwargs))  # type: ignore

    return wrap


from wraps.future_result import FutureResult
