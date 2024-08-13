"""Future either values."""

from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, TypeVar, final

from attrs import field, frozen
from funcs.decorators import wraps
from funcs.functions import identity
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
from typing_extensions import Never, ParamSpec

from wraps.either import Either, Left, Right
from wraps.futures.future import Future
from wraps.futures.reawaitable import ReAwaitable
from wraps.option import Option
from wraps.result import Result

if TYPE_CHECKING:
    from wraps.futures.typing import FutureEitherCallable
    from wraps.typing import EitherAsyncCallable

__all__ = ("FutureEither", "future_either", "future_left", "future_right", "wrap_future_either")

P = ParamSpec("P")

L = TypeVar("L", covariant=True)
R = TypeVar("R", covariant=True)

M = TypeVar("M")
S = TypeVar("S")

T = TypeVar("T")
U = TypeVar("U")


@final
@frozen()
class FutureEither(Future[Either[L, R]]):
    """[`Future[Either[L, R]]`][wraps.futures.future.Future],
    adapted to leverage future functionality.
    """

    awaitable: ReAwaitable[Either[L, R]] = field(converter=ReAwaitable[Either[L, R]])

    @classmethod
    def create(cls, awaitable: Awaitable[Either[M, S]]) -> FutureEither[M, S]:  # type: ignore[override]
        return cls(awaitable)  # type: ignore[arg-type, return-value]

    @classmethod
    def from_either(cls, either: Either[M, S]) -> FutureEither[M, S]:
        return cls.from_value(either)  # type: ignore[return-value]

    @classmethod
    def from_left(cls, value: M) -> FutureEither[M, Never]:
        return cls.from_either(Left(value))

    @classmethod
    def from_right(cls, value: S) -> FutureEither[Never, S]:
        return cls.from_either(Right(value))

    def is_left(self) -> Future[bool]:
        return super().create(self.raw_is_left())

    def is_left_and(self, predicate: Predicate[L]) -> Future[bool]:
        return super().create(self.raw_is_left_and(predicate))

    def is_left_and_await(self, predicate: AsyncPredicate[L]) -> Future[bool]:
        return super().create(self.raw_is_left_and_await(predicate))

    def is_right(self) -> Future[bool]:
        return super().create(self.raw_is_right())

    def is_right_and(self, predicate: Predicate[R]) -> Future[bool]:
        return super().create(self.raw_is_right_and(predicate))

    def is_right_and_await(self, predicate: AsyncPredicate[R]) -> Future[bool]:
        return super().create(self.raw_is_right_and_await(predicate))

    async def raw_is_left(self) -> bool:
        return (await self.awaitable).is_left()

    async def raw_is_left_and(self, predicate: Predicate[L]) -> bool:
        return (await self.awaitable).is_left_and(predicate)

    async def raw_is_left_and_await(self, predicate: AsyncPredicate[L]) -> bool:
        return await (await self.awaitable).is_left_and_await(predicate)

    async def raw_is_right(self) -> bool:
        return (await self.awaitable).is_right()

    async def raw_is_right_and(self, predicate: Predicate[R]) -> bool:
        return (await self.awaitable).is_right_and(predicate)

    async def raw_is_right_and_await(self, predicate: AsyncPredicate[R]) -> bool:
        return await (await self.awaitable).is_right_and_await(predicate)

    def expect_left(self, message: str) -> Future[L]:
        return super().create(self.raw_expect_left(message))

    def expect_right(self, message: str) -> Future[R]:
        return super().create(self.raw_expect_right(message))

    async def raw_expect_left(self, message: str) -> L:
        return (await self.awaitable).expect_left(message)

    async def raw_expect_right(self, message: str) -> R:
        return (await self.awaitable).expect_right(message)

    def unwrap_left(self) -> Future[L]:
        return super().create(self.raw_unwrap_left())

    def unwrap_right(self) -> Future[R]:
        return super().create(self.raw_unwrap_right())

    async def raw_unwrap_left(self) -> L:
        return (await self.awaitable).unwrap_left()

    async def raw_unwrap_right(self) -> R:
        return (await self.awaitable).unwrap_right()

    def left(self) -> FutureOption[L]:
        return FutureOption(self.raw_left())

    def left_or(self, default: L) -> Future[L]:  # type: ignore[misc]
        return super().create(self.raw_left_or(default))

    def left_or_else(self, default: Nullary[L]) -> Future[L]:
        return super().create(self.raw_left_or_else(default))

    def left_or_else_await(self, default: AsyncNullary[L]) -> Future[L]:
        return super().create(self.raw_left_or_else_await(default))

    async def raw_left(self) -> Option[L]:
        return (await self.awaitable).left()

    async def raw_left_or(self, default: L) -> L:  # type: ignore[misc]
        return (await self.awaitable).left_or(default)

    async def raw_left_or_else(self, default: Nullary[L]) -> L:
        return (await self.awaitable).left_or_else(default)

    async def raw_left_or_else_await(self, default: AsyncNullary[L]) -> L:
        return await (await self.awaitable).left_or_else_await(default)

    def right(self) -> FutureOption[R]:
        return FutureOption(self.raw_right())

    def right_or(self, default: R) -> Future[R]:  # type: ignore[misc]
        return super().create(self.raw_right_or(default))

    def right_or_else(self, default: Nullary[R]) -> Future[R]:
        return super().create(self.raw_right_or_else(default))

    def right_or_else_await(self, default: AsyncNullary[R]) -> Future[R]:
        return super().create(self.raw_right_or_else_await(default))

    async def raw_right(self) -> Option[R]:
        return (await self.awaitable).right()

    async def raw_right_or(self, default: R) -> R:  # type: ignore[misc]
        return (await self.awaitable).right_or(default)

    async def raw_right_or_else(self, default: Nullary[R]) -> R:
        return (await self.awaitable).right_or_else(default)

    async def raw_right_or_else_await(self, default: AsyncNullary[R]) -> R:
        return await (await self.awaitable).right_or_else_await(default)

    def into_either(self: FutureEither[T, T]) -> Future[T]:
        return super().create(self.raw_into_either())

    async def raw_into_either(self: FutureEither[T, T]) -> T:
        return (await self.awaitable).into_either()

    def inspect_left(self, inspect: Inspect[L]) -> FutureEither[L, R]:
        return self.create(self.raw_inspect_left(inspect))

    def inspect_left_await(self, inspect: AsyncInspect[L]) -> FutureEither[L, R]:
        return self.create(self.raw_inspect_left_await(inspect))

    def inspect_right(self, inspect: Inspect[R]) -> FutureEither[L, R]:
        return self.create(self.raw_inspect_right(inspect))

    def inspect_right_await(self, inspect: AsyncInspect[R]) -> FutureEither[L, R]:
        return self.create(self.raw_inspect_right_await(inspect))

    async def raw_inspect_left(self, inspect: Inspect[L]) -> Either[L, R]:
        return (await self.awaitable).inspect_left(inspect)

    async def raw_inspect_left_await(self, inspect: AsyncInspect[L]) -> Either[L, R]:
        return await (await self.awaitable).inspect_left_await(inspect)

    async def raw_inspect_right(self, inspect: Inspect[R]) -> Either[L, R]:
        return (await self.awaitable).inspect_right(inspect)

    async def raw_inspect_right_await(self, inspect: AsyncInspect[R]) -> Either[L, R]:
        return await (await self.awaitable).inspect_right_await(inspect)

    async def flip(self) -> FutureEither[R, L]:
        return self.create(self.raw_flip())

    async def raw_flip(self) -> Either[R, L]:
        return (await self.awaitable).flip()

    def map_left(self, function: Unary[L, M]) -> FutureEither[M, R]:
        return self.create(self.raw_map_left(function))

    def map_left_await(self, function: AsyncUnary[L, M]) -> FutureEither[M, R]:
        return self.create(self.raw_map_left_await(function))

    def map_right(self, function: Unary[R, S]) -> FutureEither[L, S]:
        return self.create(self.raw_map_right(function))

    def map_right_await(self, function: AsyncUnary[R, S]) -> FutureEither[L, S]:
        return self.create(self.raw_map_right_await(function))

    async def raw_map_left(self, function: Unary[L, M]) -> Either[M, R]:
        return (await self.awaitable).map_left(function)

    async def raw_map_left_await(self, function: AsyncUnary[L, M]) -> Either[M, R]:
        return await (await self.awaitable).map_left_await(function)

    async def raw_map_right(self, function: Unary[R, S]) -> Either[L, S]:
        return (await self.awaitable).map_right(function)

    async def raw_map_right_await(self, function: AsyncUnary[R, S]) -> Either[L, S]:
        return await (await self.awaitable).map_right_await(function)

    def map(self: FutureEither[T, T], function: Unary[T, U]) -> FutureEither[U, U]:
        return self.create(self.raw_map(function))

    def map_await(self: FutureEither[T, T], function: AsyncUnary[T, U]) -> FutureEither[U, U]:
        return self.create(self.raw_map_await(function))

    async def raw_map(self: FutureEither[T, T], function: Unary[T, U]) -> Either[U, U]:
        return (await self.awaitable).map(function)

    async def raw_map_await(self: FutureEither[T, T], function: AsyncUnary[T, U]) -> Either[U, U]:
        return await (await self.awaitable).map_await(function)

    def map_either(self, left: Unary[L, M], right: Unary[R, S]) -> FutureEither[M, S]:
        return self.create(self.raw_map_either(left, right))

    def map_either_await(
        self, left: AsyncUnary[L, M], right: AsyncUnary[R, S]
    ) -> FutureEither[M, S]:
        return self.create(self.raw_map_either_await(left, right))

    async def raw_map_either(self, left: Unary[L, M], right: Unary[R, S]) -> Either[M, S]:
        return (await self.awaitable).map_either(left, right)

    async def raw_map_either_await(
        self, left: AsyncUnary[L, M], right: AsyncUnary[R, S]
    ) -> Either[M, S]:
        return await (await self.awaitable).map_either_await(left, right)

    def either(self, left: Unary[L, T], right: Unary[R, T]) -> Future[T]:
        return super().create(self.raw_either(left, right))

    def either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> Future[T]:
        return super().create(self.raw_either_await(left, right))

    async def raw_either(self, left: Unary[L, T], right: Unary[R, T]) -> T:
        return (await self.awaitable).either(left, right)

    async def raw_either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> T:
        return await (await self.awaitable).either_await(left, right)

    def left_and_then(self, function: Unary[L, Either[M, R]]) -> FutureEither[M, R]:
        return self.create(self.raw_left_and_then(function))

    def left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> FutureEither[M, R]:
        return self.create(self.raw_left_and_then_await(function))

    def right_and_then(self, function: Unary[R, Either[L, S]]) -> FutureEither[L, S]:
        return self.create(self.raw_right_and_then(function))

    def right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> FutureEither[L, S]:
        return self.create(self.raw_right_and_then_await(function))

    async def raw_left_and_then(self, function: Unary[L, Either[M, R]]) -> Either[M, R]:
        return (await self.awaitable).left_and_then(function)

    async def raw_left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> Either[M, R]:
        return await (await self.awaitable).left_and_then_await(function)

    async def raw_right_and_then(self, function: Unary[R, Either[L, S]]) -> Either[L, S]:
        return (await self.awaitable).right_and_then(function)

    async def raw_right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> Either[L, S]:
        return await (await self.awaitable).right_and_then_await(function)

    def flatten_left(self: FutureEither[FutureEither[L, R], R]) -> FutureEither[L, R]:
        return self.left_and_then(identity)  # type: ignore[arg-type]

    def flatten_right(self: FutureEither[L, FutureEither[L, R]]) -> FutureEither[L, R]:
        return self.right_and_then(identity)  # type: ignore[arg-type]

    def contains_left(self, value: M) -> Future[bool]:
        return super().create(self.raw_contains_left(value))

    def contains_right(self, value: S) -> Future[bool]:
        return super().create(self.raw_contains_right(value))

    async def raw_contains_left(self, value: M) -> bool:
        return (await self.awaitable).contains_left(value)

    async def raw_contains_right(self, value: S) -> bool:
        return (await self.awaitable).contains_right(value)

    def contains(self: FutureEither[T, T], value: U) -> Future[bool]:
        return super().create(self.raw_contains(value))

    async def raw_contains(self: FutureEither[T, T], value: U) -> bool:
        return (await self.awaitable).contains(value)

    def into_result(self) -> FutureResult[L, R]:
        return FutureResult(self.raw_into_result())

    async def raw_into_result(self) -> Result[L, R]:
        return (await self.awaitable).into_result()


future_either = FutureEither.from_either
"""An alias of [`FutureEither.from_either`][wraps.futures.either.FutureEither.from_either]."""

future_left = FutureEither.from_left
"""An alias of [`FutureEither.from_left`][wraps.futures.either.FutureEither.from_left]."""

future_right = FutureEither.from_right
"""An alias of [`FutureEither.from_right`][wraps.futures.either.FutureEither.from_right]."""


def wrap_future_either(function: EitherAsyncCallable[P, L, R]) -> FutureEitherCallable[P, L, R]:
    """Wraps an asynchronous `function` returning [`Either[L, R]`][wraps.either.Either]
    into a function returning [`FutureEither[L, R]`][wraps.futures.either.FutureEither].

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureEither[L, R]:
        return FutureEither(function(*args, **kwargs))

    return wrap


from wraps.futures.option import FutureOption
from wraps.futures.result import FutureResult
