from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Callable, Generator, TypeVar

from attrs import define, field, frozen
from typing_extensions import Never, ParamSpec

from wraps.option import Null, Option, Some, is_null
from wraps.result import Error, Ok, Result, is_error, is_ok
from wraps.typing import AnyException, AsyncInspect, AsyncNullary, AsyncUnary, Inspect, Nullary, Unary

__all__ = (
    "ReAwaitable",
    "Future",
    "FutureOption",
    "FutureResult",
    "wrap_future",
    "wrap_future_option",
    "wrap_future_result",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")

V = TypeVar("V")


async def async_identity(value: V) -> V:
    return value


def identity(value: V) -> V:
    return value


@define()
class ReAwaitable(Awaitable[T]):
    """Wraps an awaitable to allow re-awaiting."""

    _awaitable: Awaitable[T] = field(repr=False)
    _option: Option[T] = field(factory=Null, repr=False, init=False)

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    @property
    async def awaitable(self) -> T:
        option = self._option

        if is_null(option):
            self._option = option = Some(await self._awaitable)

        return option.unwrap()  # when we reach here, `Some(result)` is guaranteed


@frozen()
class Future(Awaitable[T]):
    awaitable: Awaitable[T] = field(repr=False)  # should be `ReAwaitable[T]`

    def __init__(self, awaitable: Awaitable[T]) -> None:
        self.__attrs_init__(ReAwaitable(awaitable))  # type: ignore

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    @classmethod
    def create(cls, awaitable: Awaitable[U]) -> Future[U]:
        return cls(awaitable)  # type: ignore

    def map_future(self, function: Unary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to [`Future[U]`][wraps.future.Future]
        by applying `function` to the result.

        Arguments:
            function: The function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.actual_map_future(function))

    def map_future_await(self, function: AsyncUnary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to [`Future[U]`][wraps.future.Future]
        by applying an asynchronous `function` to the result.

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.actual_map_future_await(function))

    async def actual_map_future(self, function: Unary[T, U]) -> U:
        return function(await self.awaitable)

    async def actual_map_future_await(self, function: AsyncUnary[T, U]) -> U:
        return await function(await self.awaitable)

    def then(self, function: Unary[T, Future[U]]) -> Future[U]:
        """Chains computation by applying the `function` to the result, returning
        [`Future[U]`][wraps.future.Future].

        Arguments:
            function: The function returning future to apply.

        Returns:
            The resulting future.
        """
        return self.create(self.actual_then(function))

    async def actual_then(self, function: Unary[T, Future[U]]) -> U:
        return await function(await self.awaitable).awaitable

    def flatten(self: Future[Future[T]]) -> Future[T]:
        return self.then(identity)

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    async def async_iter(self) -> AsyncIterator[T]:
        """Returns an asynchronous iterator over the result of this
        [`Future[T]`][wraps.future.Future].

        Returns:
            An asynchronous iterator over the result of the future.
        """
        yield await self.awaitable

    @classmethod
    def do(cls, async_iterator: AsyncIterator[T]) -> Future[T]:
        """Returns the next value in the asynchronous iterator.

        This allows for a pattern called *do-notation*.

        Example:
            ```python
            result = await Future.do(
                x + y
                async for x in Future.from_value(4)
                async for y in Future.from_value(9)
            )

            print(result)  # 13
            ```

        Arguments:
            async_iterator: The async iterator to advance.
        """
        return cls(cls.actual_do(async_iterator))

    @classmethod
    async def actual_do(cls, async_iterator: AsyncIterator[T]) -> T:
        return await async_iterator.__anext__()

    @classmethod
    def from_value(cls, value: T) -> Future[T]:  # type: ignore
        """Wraps `value` of type `T` into [`Future[T]`][wraps.future.Future].

        This is functionally the same as:

        ```python
        async def async_identity(value: T) -> T:
            return value

        value = 42

        future = Future(async_identity(value))
        ```

        Example:
            ```python
            value = 42

            assert await Future.from_value(value) is value
            ```

        Arguments:
            value: The value to wrap.

        Returns:
            The future wrapping the given value.
        """
        return cls(async_identity(value))


@frozen()
class FutureOption(Future[Option[T]]):
    if TYPE_CHECKING:
        awaitable: Awaitable[Option[T]]  # should be `ReAwaitable[Option[T]]`

    @classmethod
    def create(cls, awaitable: Awaitable[Option[U]]) -> FutureOption[U]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_some(cls, value: T) -> FutureOption[T]:  # type: ignore
        return cls.from_value(Some(value))  # type: ignore

    @classmethod
    def from_null(cls) -> FutureOption[Never]:  # type: ignore
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

    def unwrap_or_raise(self, exception: AnyException) -> Future[T]:
        return super().create(self.actual_unwrap_or_raise(exception))

    def unwrap_or_raise_with(self, function: Nullary[AnyException]) -> Future[T]:
        return super().create(self.actual_unwrap_or_raise_with(function))

    def unwrap_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> Future[T]:
        return super().create(self.actual_unwrap_or_raise_with_await(function))

    async def actual_unwrap_or_raise(self, exception: AnyException) -> T:
        return (await self.awaitable).unwrap_or_raise(exception)

    async def actual_unwrap_or_raise_with(self, function: Nullary[AnyException]) -> T:
        return (await self.awaitable).unwrap_or_raise_with(function)

    async def actual_unwrap_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> T:
        return await (await self.awaitable).unwrap_or_raise_with_await(function)

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

    def map_await_or_else_await(self, default: AsyncNullary[U], function: AsyncUnary[T, U]) -> Future[U]:
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

    async def actual_map_await_or_else_await(self, default: AsyncNullary[U], function: AsyncUnary[T, U]) -> U:
        return await (await self.awaitable).map_await_or_else_await(default, function)


@frozen()
class FutureResult(Future[Result[T, E]]):
    if TYPE_CHECKING:
        awaitable: Awaitable[Result[T, E]]  # should be `ReAwaitable[Result[T, E]]`

    @classmethod
    def create(cls, awaitable: Awaitable[Result[U, F]]) -> FutureResult[U, F]:  # type: ignore
        return cls(awaitable)  # type: ignore

    @classmethod
    def from_ok(cls, value: T) -> FutureResult[T, Never]:  # type: ignore
        return cls.from_value(Ok(value))  # type: ignore

    @classmethod
    def from_error(cls, value: E) -> FutureResult[Never, E]:  # type: ignore
        return cls.from_value(Error(value))  # type: ignore

    def inspect(self, function: Inspect[T]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect(function))

    def inspect_error(self, function: Inspect[E]) -> FutureResult[T, E]:
        return self.create(self.actual_inspect_error(function))

    async def actual_inspect(self, function: Inspect[T]) -> Result[T, E]:
        return (await self.awaitable).inspect(function)

    async def actual_inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        return (await self.awaitable).inspect_error(function)

    def map_ok(self, function: Unary[T, U]) -> FutureResult[U, E]:
        return self.create(self.actual_map_ok(function))

    def map_error(self, function: Unary[E, F]) -> FutureResult[T, F]:
        return self.create(self.actual_map_error(function))

    async def actual_map_ok(self, function: Unary[T, U]) -> Result[U, E]:
        return (await self.awaitable).map(function)

    async def actual_map_error(self, function: Unary[E, F]) -> Result[T, F]:
        return (await self.awaitable).map_error(function)

    def map_ok_await(self, function: Unary[T, Awaitable[U]]) -> FutureResult[U, E]:
        return self.create(self.actual_map_ok_await(function))

    def map_error_await(self, function: AsyncUnary[E, F]) -> FutureResult[T, F]:
        return self.create(self.actual_map_error_await(function))

    async def actual_map_ok_await(self, function: Unary[T, Awaitable[U]]) -> Result[U, E]:
        result = await self.awaitable

        if is_ok(result):
            return result.create(await function(result.unwrap()))  # type: ignore

        return result  # type: ignore  # guaranteed `Error[E]`

    async def actual_map_error_await(self, function: Unary[E, Awaitable[F]]) -> Result[T, F]:
        result = await self.awaitable

        if is_error(result):
            return result.create(await function(result.unwrap_error()))  # type: ignore

        return result  # type: ignore  # guaranteed `Ok[T]`

    def and_then(self, function: Unary[T, FutureResult[U, E]]) -> FutureResult[U, E]:
        return self.create(self.actual_and_then(function))

    def or_else(self, function: Unary[E, FutureResult[T, F]]) -> FutureResult[T, F]:
        return self.create(self.actual_or_else(function))

    async def actual_and_then(self, function: Unary[T, FutureResult[U, E]]) -> Result[U, E]:
        result = await self.awaitable

        if is_ok(result):
            return await function(result.unwrap()).awaitable  # type: ignore

        return result  # type: ignore  # guaranteed `Error[E]`

    async def actual_or_else(self, function: Unary[E, FutureResult[T, F]]) -> Result[T, F]:
        result = await self.awaitable

        if is_error(result):
            return await function(result.unwrap_error()).awaitable  # type: ignore

        return result  # type: ignore  # guaranteed `Ok[T]`

    def try_flatten(self: FutureResult[FutureResult[T, E], E]) -> FutureResult[T, E]:
        return self.and_then(identity)

    def try_flatten_error(self: FutureResult[T, FutureResult[T, E]]) -> FutureResult[T, E]:
        return self.or_else(identity)

    def into_future(self) -> Future[Result[T, E]]:
        return super().create(self.awaitable)


def wrap_future(function: Callable[P, Awaitable[T]]) -> Callable[P, Future[T]]:
    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        return Future(function(*args, **kwargs))

    return wrap


def wrap_future_option(function: Callable[P, Awaitable[T]]) -> Callable[P, FutureOption[T]]:
    async def wrapping(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(await function(*args, **kwargs))

        except Exception:
            return Null()

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureOption[T]:
        return FutureOption(wrapping(*args, **kwargs))  # type: ignore

    return wrap


def wrap_future_result(
    function: Callable[P, Awaitable[T]]
) -> Callable[P, FutureResult[T, Exception]]:
    async def wrapping(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
        try:
            return Ok(await function(*args, **kwargs))

        except Exception as error:
            return Error(error)

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> FutureResult[T, Exception]:
        return FutureResult(wrapping(*args, **kwargs))  # type: ignore

    return wrap
