"""Future optional values."""

from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Optional, Tuple, TypeVar, final

from attrs import field, frozen
from funcs.decorators import wraps
from funcs.functions import identity
from typing_aliases import (
    AnyError,
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
from typing_extensions import Never, ParamSpec

from wraps.futures.future import Future
from wraps.futures.reawaitable import ReAwaitable
from wraps.option import NULL, Option, Some
from wraps.result import Result

if TYPE_CHECKING:
    from wraps.futures.typing import FutureOptionCallable
    from wraps.typing import OptionAsyncCallable

__all__ = ("FutureOption", "future_option", "future_some", "future_null", "wrap_future_option")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E", covariant=True)
F = TypeVar("F")


@final
@frozen()
class FutureOption(Future[Option[T]]):
    """[`Future[Option[T]]`][wraps.futures.future.Future],
    adapted to leverage future functionality.
    """

    awaitable: ReAwaitable[Option[T]] = field(converter=ReAwaitable[Option[T]])

    @classmethod
    def create(cls, awaitable: Awaitable[Option[U]]) -> FutureOption[U]:  # type: ignore[override]
        return cls(awaitable)  # type: ignore[arg-type, return-value]

    @classmethod
    def from_option(cls, option: Option[U]) -> FutureOption[U]:
        return cls.from_value(option)  # type: ignore[return-value]

    @classmethod
    def from_some(cls, value: U) -> FutureOption[U]:
        return cls.from_option(Some(value))

    @classmethod
    def from_null(cls) -> FutureOption[Never]:
        return cls.from_option(NULL)

    def is_some(self) -> Future[bool]:
        return super().create(self.raw_is_some())

    def is_some_and(self, predicate: Predicate[T]) -> Future[bool]:
        return super().create(self.raw_is_some_and(predicate))

    def is_some_and_await(self, predicate: AsyncPredicate[T]) -> Future[bool]:
        return super().create(self.raw_is_some_and_await(predicate))

    def is_null(self) -> Future[bool]:
        return super().create(self.raw_is_null())

    async def raw_is_some(self) -> bool:
        return (await self.awaitable).is_some()

    async def raw_is_some_and(self, predicate: Predicate[T]) -> bool:
        return (await self.awaitable).is_some_and(predicate)

    async def raw_is_some_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await (await self.awaitable).is_some_and_await(predicate)

    async def raw_is_null(self) -> bool:
        return (await self.awaitable).is_null()

    def expect(self, message: str) -> Future[T]:
        return super().create(self.raw_expect(message))

    async def raw_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

    def extract(self) -> Future[Optional[T]]:
        return super().create(self.raw_extract())

    async def raw_extract(self) -> Optional[T]:
        return (await self.awaitable).extract()

    def unwrap(self) -> Future[T]:
        return super().create(self.raw_unwrap())

    def unwrap_or(self, default: T) -> Future[T]:  # type: ignore[misc]
        return super().create(self.raw_unwrap_or(default))

    def unwrap_or_else(self, default: Nullary[T]) -> Future[T]:
        return super().create(self.raw_unwrap_or_else(default))

    def unwrap_or_else_await(self, default: AsyncNullary[T]) -> Future[T]:
        return super().create(self.raw_unwrap_or_else_await(default))

    async def raw_unwrap(self) -> T:
        return (await self.awaitable).unwrap()

    async def raw_unwrap_or(self, default: T) -> T:  # type: ignore[misc]
        return (await self.awaitable).unwrap_or(default)

    async def raw_unwrap_or_else(self, default: Nullary[T]) -> T:
        return (await self.awaitable).unwrap_or_else(default)

    async def raw_unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        return await (await self.awaitable).unwrap_or_else_await(default)

    def or_raise(self, error: AnyError) -> Future[T]:
        return super().create(self.raw_or_raise(error))

    def or_raise_with(self, error: Nullary[AnyError]) -> Future[T]:
        return super().create(self.raw_or_raise_with(error))

    def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> Future[T]:
        return super().create(self.raw_or_raise_with_await(error))

    async def raw_or_raise(self, error: AnyError) -> T:
        return (await self.awaitable).or_raise(error)

    async def raw_or_raise_with(self, error: Nullary[AnyError]) -> T:
        return (await self.awaitable).or_raise_with(error)

    async def raw_or_raise_with_await(self, error: AsyncNullary[AnyError]) -> T:
        return await (await self.awaitable).or_raise_with_await(error)

    def inspect(self, function: Inspect[T]) -> FutureOption[T]:
        return self.create(self.raw_inspect(function))

    def inspect_await(self, function: AsyncInspect[T]) -> FutureOption[T]:
        return self.create(self.raw_inspect_await(function))

    async def raw_inspect(self, function: Inspect[T]) -> Option[T]:
        return (await self.awaitable).inspect(function)

    async def raw_inspect_await(self, function: AsyncInspect[T]) -> Option[T]:
        return await (await self.awaitable).inspect_await(function)

    def map(self, function: Unary[T, U]) -> FutureOption[U]:
        return self.create(self.raw_map(function))

    def map_or(self, default: U, function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or(default, function))

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or_else(default, function))

    def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or_else_await(default, function))

    def map_await(self, function: AsyncUnary[T, U]) -> FutureOption[U]:
        return self.create(self.raw_map_await(function))

    def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.raw_map_await_or(default, function))

    def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.raw_map_await_or_else(default, function))

    def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> Future[U]:
        return super().create(self.raw_map_await_or_else_await(default, function))

    async def raw_map(self, function: Unary[T, U]) -> Option[U]:
        return (await self.awaitable).map(function)

    async def raw_map_or(self, default: U, function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or(default, function)

    async def raw_map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or_else(default, function)

    async def raw_map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await (await self.awaitable).map_or_else_await(default, function)

    async def raw_map_await(self, function: AsyncUnary[T, U]) -> Option[U]:
        return await (await self.awaitable).map_await(function)

    async def raw_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def raw_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def raw_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    def ok_or(self, error: F) -> FutureResult[T, F]:
        return FutureResult(self.raw_ok_or(error))

    def ok_or_else(self, error: Nullary[E]) -> FutureResult[T, E]:
        return FutureResult(self.raw_ok_or_else(error))

    def ok_or_else_await(self, error: AsyncNullary[E]) -> FutureResult[T, E]:
        return FutureResult(self.raw_ok_or_else_await(error))

    async def raw_ok_or(self, error: E) -> Result[T, E]:  # type: ignore[misc]
        return (await self.awaitable).ok_or(error)

    async def raw_ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        return (await self.awaitable).ok_or_else(error)

    async def raw_ok_or_else_await(self, error: AsyncNullary[E]) -> Result[T, E]:
        return await (await self.awaitable).ok_or_else_await(error)

    def and_then(self, function: Unary[T, Option[U]]) -> FutureOption[U]:
        return self.create(self.raw_and_then(function))

    def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> FutureOption[U]:
        return self.create(self.raw_and_then_await(function))

    def or_else(self, function: Nullary[Option[T]]) -> FutureOption[T]:
        return self.create(self.raw_or_else(function))

    def or_else_await(self, function: AsyncNullary[Option[T]]) -> FutureOption[T]:
        return self.create(self.raw_or_else_await(function))

    async def raw_and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        return (await self.awaitable).and_then(function)

    async def raw_and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Option[U]:
        return await (await self.awaitable).and_then_await(function)

    async def raw_or_else(self, function: Nullary[Option[T]]) -> Option[T]:
        return (await self.awaitable).or_else(function)

    async def raw_or_else_await(self, function: AsyncNullary[Option[T]]) -> Option[T]:
        return await (await self.awaitable).or_else_await(function)

    def filter(self, predicate: Predicate[T]) -> FutureOption[T]:
        return self.create(self.raw_filter(predicate))

    def filter_await(self, predicate: AsyncPredicate[T]) -> FutureOption[T]:
        return self.create(self.raw_filter_await(predicate))

    async def raw_filter(self, predicate: Predicate[T]) -> Option[T]:
        return (await self.awaitable).filter(predicate)

    async def raw_filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        return await (await self.awaitable).filter_await(predicate)

    def xor(self, option: FutureOption[T]) -> FutureOption[T]:
        return self.create(self.raw_xor(option))

    async def raw_xor(self, option: FutureOption[T]) -> Option[T]:
        return (await self.awaitable).xor(await option.awaitable)

    def zip(self, option: FutureOption[U]) -> FutureOption[Tuple[T, U]]:
        return self.create(self.raw_zip(option))

    def zip_with(self, option: FutureOption[U], function: Binary[T, U, V]) -> FutureOption[V]:
        return self.create(self.raw_zip_with(option, function))

    def zip_with_await(
        self, option: FutureOption[U], function: AsyncBinary[T, U, V]
    ) -> FutureOption[V]:
        return self.create(self.raw_zip_with_await(option, function))

    async def raw_zip(self, option: FutureOption[U]) -> Option[Tuple[T, U]]:
        return (await self.awaitable).zip(await option.awaitable)

    async def raw_zip_with(self, option: FutureOption[U], function: Binary[T, U, V]) -> Option[V]:
        return (await self.awaitable).zip_with(await option.awaitable, function)

    async def raw_zip_with_await(
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
        return self.create(self.raw_flatten())

    async def raw_flatten(self: FutureOption[FutureOption[U]]) -> Option[U]:
        return await self.and_then_await(identity)

    def contains(self, value: U) -> Future[bool]:
        return super().create(self.raw_contains(value))

    async def raw_contains(self, value: U) -> bool:
        return (await self.awaitable).contains(value)

    def early(self) -> Future[T]:
        return super().create(self.raw_early())

    async def raw_early(self) -> T:
        return (await self.awaitable).early()


future_option = FutureOption.from_option
"""An alias of [`FutureOption.from_option`][wraps.futures.option.FutureOption.from_option]."""

future_some = FutureOption.from_some
"""An alias of [`FutureOption.from_some`][wraps.futures.option.FutureOption.from_some]."""

future_null = FutureOption.from_null
"""An alias of [`FutureOption.from_null`][wraps.futures.option.FutureOption.from_null]."""


def wrap_future_option(function: OptionAsyncCallable[P, T]) -> FutureOptionCallable[P, T]:
    """Wraps an asynchronous `function` returning [`Option[T]`][wraps.option.Option] into a function
    returning [`FutureOption[T]`][wraps.futures.option.FutureOption].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureOption[T]:
        return FutureOption(function(*args, **kwargs))

    return wrap


from wraps.futures.result import FutureResult
