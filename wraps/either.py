"""Either values.

The [`Either[L, R]`][wraps.either.Either] type is symmetric and treats its variants the same way,
without preference.
For representing results (values and errors), use the [`Result[T, E]`][wraps.result.Result] instead.
"""

from __future__ import annotations

from abc import abstractmethod as required
from typing import AsyncIterator, Iterator, TypeVar, Union

from attrs import frozen
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
from typing_extensions import Literal, Never, Protocol, TypeGuard, final

from wraps.errors import panic
from wraps.option import Null, Option, Some
from wraps.utils import async_empty, async_once, empty, identity, once

__all__ = ("Either", "Left", "Right", "is_left", "is_right")

L = TypeVar("L", covariant=True)
M = TypeVar("M")
R = TypeVar("R", covariant=True)
S = TypeVar("S")

T = TypeVar("T")
U = TypeVar("U")

E = TypeVar("E")


class EitherProtocol(Protocol[L, R]):  # type: ignore[misc]
    @required
    def is_left(self) -> bool:
        ...

    @required
    def is_left_and(self, predicate: Predicate[L]) -> bool:
        ...

    @required
    async def is_left_and_await(self, predicate: AsyncPredicate[L]) -> bool:
        ...

    @required
    def is_right(self) -> bool:
        ...

    @required
    def is_right_and(self, predicate: Predicate[R]) -> bool:
        ...

    @required
    async def is_right_and_await(self, predicate: AsyncPredicate[R]) -> bool:
        ...

    @required
    def expect_left(self, message: str) -> L:
        ...

    @required
    def expect_right(self, message: str) -> R:
        ...

    @required
    def unwrap_left(self) -> L:
        ...

    @required
    def unwrap_right(self) -> R:
        ...

    @required
    def left(self) -> Option[L]:
        ...

    @required
    def left_or(self, default: L) -> L:  # type: ignore
        ...

    @required
    def left_or_else(self, default: Nullary[L]) -> L:
        ...

    @required
    async def left_or_else_await(self, default: AsyncNullary[L]) -> L:
        ...

    @required
    def right(self) -> Option[R]:
        ...

    @required
    def right_or(self, default: R) -> R:  # type: ignore
        ...

    @required
    def right_or_else(self, default: Nullary[R]) -> R:
        ...

    @required
    async def right_or_else_await(self, default: AsyncNullary[R]) -> R:
        ...

    @required
    def into_either(self: EitherProtocol[T, T]) -> T:
        ...

    @required
    def inspect_left(self, function: Inspect[L]) -> Either[L, R]:
        ...

    @required
    def inspect_right(self, function: Inspect[R]) -> Either[L, R]:
        ...

    @required
    async def inspect_left_await(self, function: AsyncInspect[L]) -> Either[L, R]:
        ...

    @required
    async def inspect_right_await(self, function: AsyncInspect[R]) -> Either[L, R]:
        ...

    @required
    def flip(self) -> Either[R, L]:
        ...

    @required
    def map_left(self, function: Unary[L, M]) -> Either[M, R]:
        ...

    @required
    async def map_left_await(self, function: AsyncUnary[L, M]) -> Either[M, R]:
        ...

    @required
    def map_right(self, function: Unary[R, S]) -> Either[L, S]:
        ...

    @required
    async def map_right_await(self, function: AsyncUnary[R, S]) -> Either[L, S]:
        ...

    @required
    def map(self: EitherProtocol[T, T], function: Unary[T, U]) -> Either[U, U]:
        ...

    @required
    async def map_await(self: EitherProtocol[T, T], function: AsyncUnary[T, U]) -> Either[U, U]:
        ...

    @required
    def either(self, left: Unary[L, T], right: Unary[R, T]) -> T:
        ...

    @required
    async def either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> T:
        ...

    @required
    def left_and_then(self, function: Unary[L, Either[M, R]]) -> Either[M, R]:
        ...

    @required
    async def left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> Either[M, R]:
        ...

    @required
    def right_and_then(self, function: Unary[R, Either[L, S]]) -> Either[L, S]:
        ...

    @required
    async def right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> Either[L, S]:
        ...

    @required
    def iter_left(self) -> Iterator[L]:
        ...

    @required
    def iter_right(self) -> Iterator[R]:
        ...

    @required
    def iter_either(self: EitherProtocol[T, T]) -> Iterator[T]:
        ...

    @required
    def async_iter_left(self) -> AsyncIterator[L]:
        ...

    @required
    def async_iter_right(self) -> AsyncIterator[R]:
        ...

    @required
    def async_iter_either(self: EitherProtocol[T, T]) -> AsyncIterator[T]:
        ...

    def flatten_left(self: EitherProtocol[EitherProtocol[L, R], R]) -> Either[L, R]:
        return self.left_and_then(identity)  # type: ignore

    def flatten_right(self: EitherProtocol[L, EitherProtocol[L, R]]) -> Either[L, R]:
        return self.right_and_then(identity)  # type: ignore

    # @required
    # def factor_null(self: EitherProtocol[Option[L], Option[R]]) -> Option[Either[L, R]]:
    #     ...

    # @required
    # def factor_error(self: EitherProtocol[Result[L, E], Result[R, E]]) -> Result[Either[L, R], E]:
    #     ...

    # @required
    # def factor_ok(self: EitherProtocol[Result[T, L], Result[T, R]]) -> Result[T, Either[L, R]]:
    #     ...

    @required
    def contains_left(self, value: M) -> bool:
        ...

    @required
    def contains_right(self, value: S) -> bool:
        ...

    @required
    def contains(self: EitherProtocol[T, T], value: U) -> bool:
        ...

    @required
    def into_result(self) -> Result[L, R]:
        ...


UNWRAP_LEFT_ON_RIGHT = "`unwrap_left` called on right"
UNWRAP_RIGHT_ON_LEFT = "`unwrap_right` called on left"


@final
@frozen()
class Left(EitherProtocol[L, Never]):
    """[`Left[L]`][wraps.either.Left] variant of [`Either[L, R]`][wraps.either.Either]."""

    value: L

    @classmethod
    def create(cls, value: M) -> Left[M]:
        return cls(value)  # type: ignore

    def is_left(self) -> Literal[True]:
        return True

    def is_left_and(self, predicate: Predicate[L]) -> bool:
        return predicate(self.value)

    async def is_left_and_await(self, predicate: AsyncPredicate[L]) -> bool:
        return await predicate(self.value)

    def is_right(self) -> Literal[False]:
        return False

    def is_right_and(self, predicate: Predicate[R]) -> Literal[False]:
        return False

    async def is_right_and_await(self, predicate: AsyncPredicate[R]) -> Literal[False]:
        return False

    def left(self) -> Some[L]:
        return Some(self.value)

    def left_or(self, default: L) -> L:  # type: ignore
        return self.value

    def left_or_else(self, default: Nullary[L]) -> L:
        return self.value

    async def left_or_else_await(self, default: AsyncNullary[L]) -> L:
        return self.value

    def right(self) -> Null:
        return Null()

    def right_or(self, default: R) -> R:  # type: ignore
        return default

    def right_or_else(self, default: Nullary[R]) -> R:
        return default()

    async def right_or_else_await(self, default: AsyncNullary[R]) -> R:
        return await default()

    def expect_left(self, message: str) -> L:
        return self.value

    def expect_right(self, message: str) -> Never:
        panic(message)

    def unwrap_left(self) -> L:
        return self.value

    def unwrap_right(self) -> Never:
        panic(UNWRAP_RIGHT_ON_LEFT)

    def into_either(self: Left[T]) -> T:
        return self.value

    def inspect_left(self, function: Inspect[L]) -> Left[L]:
        function(self.value)

        return self

    def inspect_right(self, function: Inspect[R]) -> Left[L]:
        return self

    async def inspect_left_await(self, function: AsyncInspect[L]) -> Left[L]:
        await function(self.value)

        return self

    async def inspect_right_await(self, function: AsyncInspect[R]) -> Left[L]:
        return self

    def flip(self) -> Right[L]:
        return Right(self.value)

    def map_left(self, function: Unary[L, M]) -> Left[M]:
        return self.create(function(self.value))

    async def map_left_await(self, function: AsyncUnary[L, M]) -> Left[M]:
        return self.create(await function(self.value))

    def map_right(self, function: Unary[R, S]) -> Left[L]:
        return self

    async def map_right_await(self, function: AsyncUnary[R, S]) -> Left[L]:
        return self

    def map(self: Left[T], function: Unary[T, U]) -> Left[U]:
        return self.create(function(self.value))

    async def map_await(self: Left[T], function: AsyncUnary[T, U]) -> Left[U]:
        return self.create(await function(self.value))

    def either(self, left: Unary[L, T], right: Unary[R, T]) -> T:
        return left(self.value)

    async def either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> T:
        return await left(self.value)

    def left_and_then(self, function: Unary[L, Either[M, R]]) -> Either[M, R]:
        return function(self.value)

    async def left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> Either[M, R]:
        return await function(self.value)

    def right_and_then(self, function: Unary[R, Either[L, S]]) -> Left[L]:
        return self

    async def right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> Left[L]:
        return self

    def iter_left(self) -> Iterator[L]:
        return once(self.value)

    def iter_right(self) -> Iterator[Never]:
        return empty()

    def iter_either(self: Left[T]) -> Iterator[T]:
        return once(self.value)

    def async_iter_left(self) -> AsyncIterator[L]:
        return async_once(self.value)

    def async_iter_right(self) -> AsyncIterator[Never]:
        return async_empty()

    def async_iter_either(self: Left[T]) -> AsyncIterator[T]:
        return async_once(self.value)

    def contains_left(self, value: M) -> bool:
        return self.value == value

    def contains_right(self, value: S) -> Literal[False]:
        return False

    def contains(self: Left[T], value: U) -> bool:
        return self.value == value

    def into_result(self) -> Ok[L]:
        return Ok(self.value)


@final
@frozen()
class Right(EitherProtocol[Never, R]):
    """[`Right[R]`][wraps.either.Right] variant of [`Either[L, R]`][wraps.either.Either]."""

    value: R

    @classmethod
    def create(cls, value: S) -> Right[S]:
        return cls(value)  # type: ignore

    def is_left(self) -> Literal[False]:
        return False

    def is_left_and(self, predicate: Predicate[L]) -> Literal[False]:
        return False

    async def is_left_and_await(self, predicate: AsyncPredicate[L]) -> Literal[False]:
        return False

    def is_right(self) -> Literal[True]:
        return True

    def is_right_and(self, predicate: Predicate[R]) -> bool:
        return predicate(self.value)

    async def is_right_and_await(self, predicate: AsyncPredicate[R]) -> bool:
        return await predicate(self.value)

    def left(self) -> Null:
        return Null()

    def left_or(self, default: L) -> L:  # type: ignore
        return default

    def left_or_else(self, default: Nullary[L]) -> L:
        return default()

    async def left_or_else_await(self, default: AsyncNullary[L]) -> L:
        return await default()

    def right(self) -> Some[R]:
        return Some(self.value)

    def right_or(self, default: R) -> R:  # type: ignore
        return self.value

    def right_or_else(self, default: Nullary[R]) -> R:
        return self.value

    async def right_or_else_await(self, default: AsyncNullary[R]) -> R:
        return self.value

    def expect_left(self, message: str) -> Never:
        panic(message)

    def expect_right(self, message: str) -> R:
        return self.value

    def unwrap_left(self) -> Never:
        panic(UNWRAP_LEFT_ON_RIGHT)

    def unwrap_right(self) -> R:
        return self.value

    def into_either(self: Right[T]) -> T:
        return self.value

    def inspect_left(self, function: Inspect[L]) -> Right[R]:
        return self

    def inspect_right(self, function: Inspect[R]) -> Right[R]:
        function(self.value)

        return self

    async def inspect_left_await(self, function: AsyncInspect[L]) -> Right[R]:
        return self

    async def inspect_right_await(self, function: AsyncInspect[R]) -> Right[R]:
        await function(self.value)

        return self

    def flip(self) -> Left[R]:
        return Left(self.value)

    def map_left(self, function: Unary[L, M]) -> Right[R]:
        return self

    async def map_left_await(self, function: AsyncUnary[L, M]) -> Right[R]:
        return self

    def map_right(self, function: Unary[R, S]) -> Right[S]:
        return self.create(function(self.value))

    async def map_right_await(self, function: AsyncUnary[R, S]) -> Right[S]:
        return self.create(await function(self.value))

    def map(self: Right[T], function: Unary[T, U]) -> Right[U]:
        return self.create(function(self.value))

    async def map_await(self: Right[T], function: AsyncUnary[T, U]) -> Right[U]:
        return self.create(await function(self.value))

    def either(self, left: Unary[L, T], right: Unary[R, T]) -> T:
        return right(self.value)

    async def either_await(self, left: AsyncUnary[L, T], right: AsyncUnary[R, T]) -> T:
        return await right(self.value)

    def left_and_then(self, function: Unary[L, Either[M, R]]) -> Right[R]:
        return self

    async def left_and_then_await(self, function: AsyncUnary[L, Either[M, R]]) -> Right[R]:
        return self

    def right_and_then(self, function: Unary[R, Either[L, S]]) -> Either[L, S]:
        return function(self.value)

    async def right_and_then_await(self, function: AsyncUnary[R, Either[L, S]]) -> Either[L, S]:
        return await function(self.value)

    def iter_left(self) -> Iterator[Never]:
        return empty()

    def iter_right(self) -> Iterator[R]:
        return once(self.value)

    def iter_either(self: Right[T]) -> Iterator[T]:
        return once(self.value)

    def async_iter_left(self) -> AsyncIterator[Never]:
        return async_empty()

    def async_iter_right(self) -> AsyncIterator[R]:
        return async_once(self.value)

    def async_iter_either(self: Right[T]) -> AsyncIterator[T]:
        return async_once(self.value)

    def contains_left(self, value: M) -> Literal[False]:
        return False

    def contains_right(self, value: S) -> bool:
        return self.value == value

    def contains(self: Right[T], value: U) -> bool:
        return self.value == value

    def into_result(self) -> Error[R]:
        return Error(self.value)


Either = Union[Left[L], Right[R]]
"""Either value, expressed as the union of [`Left[L]`][wraps.either.Left]
and [`Right[R]`][wraps.either.Right].
"""


def is_left(either: Either[L, R]) -> TypeGuard[Left[L]]:
    return either.is_left()


def is_right(either: Either[L, R]) -> TypeGuard[Right[R]]:
    return either.is_right()


# import cycle solution
from wraps.result import Error, Ok, Result
