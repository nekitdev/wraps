"""Future error handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, TypeVar, final

from attrs import field, frozen
from funcs.decorators import wraps
from funcs.functions import identity
from typing_aliases import (
    AnyError,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)
from typing_extensions import Never, ParamSpec

from wraps.either import Either
from wraps.futures.future import Future
from wraps.futures.reawaitable import ReAwaitable
from wraps.option import Option
from wraps.result import Error, Ok, Result

if TYPE_CHECKING:
    from wraps.futures.typing import FutureResultCallable
    from wraps.typing import ResultAsyncCallable

__all__ = ("FutureResult", "future_result", "future_ok", "future_error", "wrap_future_result")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")

V = TypeVar("V")


@final
@frozen()
class FutureResult(Future[Result[T, E]]):
    """[`Future[Result[T, E]]`][wraps.futures.future.Future],
    adapted to leverage future functionality.
    """

    awaitable: ReAwaitable[Result[T, E]] = field(converter=ReAwaitable[Result[T, E]])

    @classmethod
    def create(cls, awaitable: Awaitable[Result[U, F]]) -> FutureResult[U, F]:  # type: ignore[override]
        return cls(awaitable)  # type: ignore[arg-type, return-value]

    @classmethod
    def from_result(cls, result: Result[U, F]) -> FutureResult[U, F]:
        return cls.from_value(result)  # type: ignore[return-value]

    @classmethod
    def from_ok(cls, value: U) -> FutureResult[U, Never]:
        return cls.from_result(Ok(value))

    @classmethod
    def from_error(cls, value: F) -> FutureResult[Never, F]:
        return cls.from_result(Error(value))

    def is_ok(self) -> Future[bool]:
        return super().create(self.raw_is_ok())

    def is_ok_and(self, predicate: Predicate[T]) -> Future[bool]:
        return super().create(self.raw_is_ok_and(predicate))

    def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> Future[bool]:
        return super().create(self.raw_is_ok_and_await(predicate))

    async def raw_is_ok(self) -> bool:
        return (await self.awaitable).is_ok()

    async def raw_is_ok_and(self, predicate: Predicate[T]) -> bool:
        return (await self.awaitable).is_ok_and(predicate)

    async def raw_is_ok_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await (await self.awaitable).is_ok_and_await(predicate)

    def is_error(self) -> Future[bool]:
        return super().create(self.raw_is_error())

    def is_error_and(self, predicate: Predicate[E]) -> Future[bool]:
        return super().create(self.raw_is_error_and(predicate))

    def is_error_and_await(self, predicate: AsyncPredicate[E]) -> Future[bool]:
        return super().create(self.raw_is_error_and_await(predicate))

    async def raw_is_error(self) -> bool:
        return (await self.awaitable).is_error()

    async def raw_is_error_and(self, predicate: Predicate[E]) -> bool:
        return (await self.awaitable).is_error_and(predicate)

    async def raw_is_error_and_await(self, predicate: AsyncPredicate[E]) -> bool:
        return await (await self.awaitable).is_error_and_await(predicate)

    def expect(self, message: str) -> Future[T]:
        return super().create(self.raw_expect(message))

    def expect_error(self, message: str) -> Future[E]:
        return super().create(self.raw_expect_error(message))

    async def raw_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

    async def raw_expect_error(self, message: str) -> E:
        return (await self.awaitable).expect_error(message)

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

    def unwrap_error(self) -> Future[E]:
        return super().create(self.raw_unwrap_error())

    def unwrap_error_or(self, default: E) -> Future[E]:  # type: ignore[misc]
        return super().create(self.raw_unwrap_error_or(default))

    def unwrap_error_or_else(self, default: Nullary[E]) -> Future[E]:
        return super().create(self.raw_unwrap_error_or_else(default))

    def unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> Future[E]:
        return super().create(self.raw_unwrap_error_or_else_await(default))

    async def raw_unwrap_error(self) -> E:
        return (await self.awaitable).unwrap_error()

    async def raw_unwrap_error_or(self, default: E) -> E:  # type: ignore[misc]
        return (await self.awaitable).unwrap_error_or(default)

    async def raw_unwrap_error_or_else(self, default: Nullary[E]) -> E:
        return (await self.awaitable).unwrap_error_or_else(default)

    async def raw_unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> E:
        return await (await self.awaitable).unwrap_error_or_else_await(default)

    def raising(self: FutureResult[T, AnyError]) -> Future[T]:
        return super().create(self.raw_raising())

    async def raw_raising(self: FutureResult[T, AnyError]) -> T:
        return (await self.awaitable).raising()

    def ok(self) -> FutureOption[T]:
        return FutureOption(self.raw_ok())

    def error(self) -> FutureOption[E]:
        return FutureOption(self.raw_error())

    async def raw_ok(self) -> Option[T]:
        return (await self.awaitable).ok()

    async def raw_error(self) -> Option[E]:
        return (await self.awaitable).error()

    def inspect(self, function: Inspect[T]) -> FutureResult[T, E]:
        return self.create(self.raw_inspect(function))

    def inspect_error(self, function: Inspect[E]) -> FutureResult[T, E]:
        return self.create(self.raw_inspect_error(function))

    def inspect_await(self, function: AsyncInspect[T]) -> FutureResult[T, E]:
        return self.create(self.raw_inspect_await(function))

    def inspect_error_await(self, function: AsyncInspect[E]) -> FutureResult[T, E]:
        return self.create(self.raw_inspect_error_await(function))

    async def raw_inspect(self, function: Inspect[T]) -> Result[T, E]:
        return (await self.awaitable).inspect(function)

    async def raw_inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        return (await self.awaitable).inspect_error(function)

    async def raw_inspect_await(self, function: AsyncInspect[T]) -> Result[T, E]:
        return await (await self.awaitable).inspect_await(function)

    async def raw_inspect_error_await(self, function: AsyncInspect[E]) -> Result[T, E]:
        return await (await self.awaitable).inspect_error_await(function)

    def map(self, function: Unary[T, U]) -> FutureResult[U, E]:
        return self.create(self.raw_map(function))

    def map_or(self, default: U, function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or(default, function))

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or_else(default, function))

    def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.raw_map_or_else_await(default, function))

    def map_error(self, function: Unary[E, F]) -> FutureResult[T, F]:
        return self.create(self.raw_map_error(function))

    def map_error_or(self, default: F, function: Unary[E, F]) -> Future[F]:
        return super().create(self.raw_map_error_or(default, function))

    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> Future[F]:
        return super().create(self.raw_map_error_or_else(default, function))

    def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> Future[F]:
        return super().create(self.raw_map_error_or_else_await(default, function))

    async def raw_map(self, function: Unary[T, U]) -> Result[U, E]:
        return (await self.awaitable).map(function)

    async def raw_map_or(self, default: U, function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or(default, function)

    async def raw_map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return (await self.awaitable).map_or_else(default, function)

    async def raw_map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await (await self.awaitable).map_or_else_await(default, function)

    async def raw_map_error(self, function: Unary[E, F]) -> Result[T, F]:
        return (await self.awaitable).map_error(function)

    async def raw_map_error_or(self, default: F, function: Unary[E, F]) -> F:
        return (await self.awaitable).map_error_or(default, function)

    async def raw_map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return (await self.awaitable).map_error_or_else(default, function)

    async def raw_map_error_or_else_await(
        self, default: AsyncNullary[F], function: Unary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_or_else_await(default, function)

    def map_await(self, function: AsyncUnary[T, U]) -> FutureResult[U, E]:
        return self.create(self.raw_map_await(function))

    def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.raw_map_await_or(default, function))

    def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.raw_map_await_or_else(default, function))

    def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> Future[U]:
        return super().create(self.raw_map_await_or_else_await(default, function))

    def map_error_await(self, function: AsyncUnary[E, F]) -> FutureResult[T, F]:
        return self.create(self.raw_map_error_await(function))

    def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> Future[F]:
        return super().create(self.raw_map_error_await_or(default, function))

    def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> Future[F]:
        return super().create(self.raw_map_error_await_or_else(default, function))

    def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> Future[F]:
        return super().create(self.raw_map_error_await_or_else_await(default, function))

    async def raw_map_await(self, function: AsyncUnary[T, U]) -> Result[U, E]:
        return await (await self.awaitable).map_await(function)

    async def raw_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def raw_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def raw_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    async def raw_map_error_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        return await (await self.awaitable).map_error_await(function)

    async def raw_map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return await (await self.awaitable).map_error_await_or(default, function)

    async def raw_map_error_await_or_else(
        self, default: Nullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_await_or_else(default, function)

    async def raw_map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await (await self.awaitable).map_error_await_or_else_await(default, function)

    def and_then(self, function: Unary[T, Result[U, E]]) -> FutureResult[U, E]:
        return self.create(self.raw_and_then(function))

    def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> FutureResult[U, E]:
        return self.create(self.raw_and_then_await(function))

    def or_else(self, function: Unary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.create(self.raw_or_else(function))

    def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.create(self.raw_or_else_await(function))

    async def raw_and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return (await self.awaitable).and_then(function)

    async def raw_and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        return await (await self.awaitable).and_then_await(function)

    async def raw_or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return (await self.awaitable).or_else(function)

    async def raw_or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await (await self.awaitable).or_else_await(function)

    def try_flatten(self: FutureResult[FutureResult[T, E], E]) -> FutureResult[T, E]:
        return self.and_then_await(identity)

    def try_flatten_error(self: FutureResult[T, FutureResult[T, E]]) -> FutureResult[T, E]:
        return self.or_else_await(identity)

    def contains(self, value: U) -> Future[bool]:
        return super().create(self.raw_contains(value))

    async def raw_contains(self, value: U) -> bool:
        return (await self.awaitable).contains(value)

    def contains_error(self, error: F) -> Future[bool]:
        return super().create(self.raw_contains_error(error))

    async def raw_contains_error(self, error: F) -> bool:
        return (await self.awaitable).contains_error(error)

    def flip(self) -> FutureResult[E, T]:
        return self.create(self.raw_flip())

    async def raw_flip(self) -> Result[E, T]:
        return (await self.awaitable).flip()

    def into_ok_or_error(self: FutureResult[T, T]) -> Future[T]:
        return super().create(self.raw_into_ok_or_error())

    async def raw_into_ok_or_error(self: FutureResult[T, T]) -> T:
        return (await self.awaitable).into_ok_or_error()

    def into_either(self) -> FutureEither[T, E]:
        return FutureEither.create(self.raw_into_either())

    async def raw_into_either(self) -> Either[T, E]:
        return (await self.awaitable).into_either()

    def early(self) -> Future[T]:
        return super().create(self.raw_early())

    async def raw_early(self) -> T:
        return (await self.awaitable).early()

    def into_future(self) -> Future[Result[T, E]]:
        return super().create(self.awaitable)


future_result = FutureResult.from_result
"""An alias of [`FutureResult.from_result`][wraps.futures.result.FutureResult.from_result]."""

future_ok = FutureResult.from_ok
"""An alias of [`FutureResult.from_ok`][wraps.futures.result.FutureResult.from_ok]."""

future_error = FutureResult.from_error
"""An alias of [`FutureResult.from_error`][wraps.futures.result.FutureResult.from_error]."""


def wrap_future_result(function: ResultAsyncCallable[P, T, E]) -> FutureResultCallable[P, T, E]:
    """Wraps an asynchronous `function` returning [`Result[T, E]`][wraps.result.Result]
    into a function returning [`FutureResult[T, E]`][wraps.futures.result.FutureResult].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureResult[T, E]:
        return FutureResult(function(*args, **kwargs))

    return wrap


from wraps.futures.either import FutureEither
from wraps.futures.option import FutureOption
