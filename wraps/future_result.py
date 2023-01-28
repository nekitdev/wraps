from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from attrs import field, frozen
from typing_extensions import Never, ParamSpec

from wraps.future import Future, ReAwaitable
from wraps.option import Option
from wraps.result import Error, Ok, Result, is_error, is_ok
from wraps.typing import AsyncInspect, AsyncNullary, AsyncUnary, Inspect, Nullary, Unary
from wraps.utils import identity

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")


V = TypeVar("V")


@frozen()
class FutureResult(Future[Result[T, E]]):
    """[`Future[Result[T, E]]`][wraps.future.Future], adapted to leverage future functionality."""

    awaitable: ReAwaitable[Result[T, E]] = field(repr=False, converter=ReAwaitable)

    @classmethod
    def create(cls, awaitable: Awaitable[Result[U, F]]) -> FutureResult[U, F]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_ok(cls, value: U) -> FutureResult[U, Never]:
        return cls.from_value(Ok(value))  # type: ignore

    @classmethod
    def from_error(cls, value: F) -> FutureResult[Never, F]:
        return cls.from_value(Error(value))  # type: ignore

    def expect(self, message: str) -> Future[T]:
        return super().create(self.actual_expect(message))

    def expect_error(self, message: str) -> Future[E]:
        return super().create(self.actual_expect_error(message))

    async def actual_expect(self, message: str) -> T:
        return (await self.awaitable).expect(message)

    async def actual_expect_error(self, message: str) -> E:
        return (await self.awaitable).expect_error(message)

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

    def unwrap_error(self) -> Future[E]:
        return super().create(self.actual_unwrap_error())

    def unwrap_error_or(self, default: E) -> Future[E]:  # type: ignore
        return super().create(self.actual_unwrap_error_or(default))

    def unwrap_error_or_else(self, default: Nullary[E]) -> Future[E]:
        return super().create(self.actual_unwrap_error_or_else(default))

    def unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> Future[E]:
        return super().create(self.actual_unwrap_error_or_else_await(default))

    async def actual_unwrap_error(self) -> E:
        return (await self.awaitable).unwrap_error()

    async def actual_unwrap_error_or(self, default: E) -> E:  # type: ignore
        return (await self.awaitable).unwrap_error_or(default)

    async def actual_unwrap_error_or_else(self, default: Nullary[E]) -> E:
        return (await self.awaitable).unwrap_error_or_else(default)

    async def actual_unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> E:
        return await (await self.awaitable).unwrap_error_or_else_await(default)

    def ok(self) -> FutureOption[T]:
        return FutureOption.create(self.actual_ok())

    def error(self) -> FutureOption[E]:
        return FutureOption.create(self.actual_error())

    async def actual_ok(self) -> Option[T]:
        return (await self.awaitable).ok()

    async def actual_error(self) -> Option[E]:
        return (await self.awaitable).error()

    def inspect(self, function: Inspect[T]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect(function))

    def inspect_error(self, function: Inspect[E]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect_error(function))

    def inspect_await(self, function: AsyncInspect[T]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect_await(function))

    def inspect_error_await(self, function: AsyncInspect[E]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect_error_await(function))

    async def actual_inspect(self, function: Inspect[T]) -> Result[T, E]:
        return (await self.awaitable).inspect(function)

    async def actual_inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        return (await self.awaitable).inspect_error(function)

    async def actual_inspect_await(self, function: AsyncInspect[T]) -> Result[T, E]:
        return await (await self.awaitable).inspect_await(function)  # type: ignore

    async def actual_inspect_error_await(self, function: AsyncInspect[E]) -> Result[T, E]:
        return await (await self.awaitable).inspect_error_await(function)  # type: ignore

    def map(self, function: Unary[T, U]) -> FutureResult[U, E]:
        return self.create(self.actual_map(function))

    def map_or(self, default: U, function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or(default, function))

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or_else(default, function))

    def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> Future[U]:
        return super().create(self.actual_map_or_else_await(default, function))

    def map_error(self, function: Unary[E, F]) -> FutureResult[T, F]:
        return self.create(self.actual_map_error(function))

    def map_error_or(self, default: F, function: Unary[E, F]) -> Future[F]:
        return super().create(self.actual_map_error_or(default, function))

    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> Future[F]:
        return super().create(self.actual_map_error_or_else(default, function))

    def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> Future[F]:
        return super().create(self.actual_map_error_or_else_await(default, function))

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
        return self.create(self.actual_map_await(function))

    def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.actual_map_await_or(default, function))

    def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> Future[U]:
        return super().create(self.actual_map_await_or_else(default, function))

    def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> Future[U]:
        return super().create(self.actual_map_await_or_else_await(default, function))

    def map_error_await(self, function: AsyncUnary[E, F]) -> FutureResult[T, F]:
        return self.create(self.actual_map_error_await(function))

    def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> Future[F]:
        return super().create(self.actual_map_error_await_or(default, function))

    def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> Future[F]:
        return super().create(self.actual_map_error_await_or_else(default, function))

    def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> Future[F]:
        return super().create(self.actual_map_error_await_or_else_await(default, function))

    async def actual_map_await(self, function: AsyncUnary[T, U]) -> Result[U, E]:
        return await (await self.awaitable).map_await(function)  # type: ignore

    async def actual_map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or(default, function)

    async def actual_map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else(default, function)

    async def actual_map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)

    async def actual_map_error_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        return await (await self.awaitable).map_error_await(function)  # type: ignore

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
        return self.create(self.actual_and_then(function))

    def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> FutureResult[U, E]:
        return self.create(self.actual_and_then_await(function))

    def or_else(self, function: Unary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.create(self.actual_or_else(function))

    def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> FutureResult[T, F]:
        return self.create(self.actual_or_else_await(function))

    async def actual_and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return (await self.awaitable).and_then(function)

    async def actual_and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        return await (await self.awaitable).and_then_await(function)

    async def actual_or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return (await self.awaitable).or_else(function)

    async def actual_or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await (await self.awaitable).or_else_await(function)

    def and_then_future(self, function: Unary[T, FutureResult[U, E]]) -> FutureResult[U, E]:
        return self.create(self.actual_and_then_future(function))

    def or_else_future(self, function: Unary[E, FutureResult[T, F]]) -> FutureResult[T, F]:
        return self.create(self.actual_or_else_future(function))

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
        return self.create(self.actual_flip())

    async def actual_flip(self) -> Result[E, T]:
        return (await self.awaitable).flip()

    def into_ok_or_error(self: FutureResult[T, T]) -> Future[T]:
        return super().create(self.actual_into_ok_or_error())

    async def actual_into_ok_or_error(self: FutureResult[T, T]) -> T:
        return (await self.awaitable).into_ok_or_error()

    def into_future(self) -> Future[Result[T, E]]:
        return super().create(self.awaitable)


P = ParamSpec("P")


def wrap_future_result(
    function: Callable[P, Awaitable[T]]
) -> Callable[P, FutureResult[T, Exception]]:
    """Wraps an asynchronous `function` returning `T` into a function returning
    [`FutureResult[T, Exception]`][wraps.future_result.FutureResult].

    This handles exceptions via returning [`Error(error)`][wraps.result.Error] on `error`,
    wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

    Example:
        ```python
        @wrap_future_result
        async def identity(value: T) -> T:
            return value

        value = 13

        assert await identity(value).unwrap() == value
        ```

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The wrapping function.
    """

    async def wrapping(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
        try:
            return Ok(await function(*args, **kwargs))

        except Exception as error:
            return Error(error)

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureResult[T, Exception]:
        return FutureResult(wrapping(*args, **kwargs))  # type: ignore

    return wrap


from wraps.future_option import FutureOption
