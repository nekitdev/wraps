from __future__ import annotations

from functools import wraps
from typing import AsyncIterator, Awaitable, Callable, Generator, TypeVar

from attrs import define, field, frozen
from typing_extensions import ParamSpec

from wraps.option import Null, Option, Some, is_null
from wraps.typing import AsyncUnary, Unary

__all__ = ("ReAwaitable", "Future", "wrap_future")

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

    def then_future(self, function: Unary[T, Future[U]]) -> Future[U]:
        """Chains computation by applying the `function` to the result, returning
        [`Future[U]`][wraps.future.Future].

        Arguments:
            function: The function returning future to apply.

        Returns:
            The resulting future.
        """
        return self.create(self.actual_then_future(function))

    async def actual_then_future(self, function: Unary[T, Future[U]]) -> U:
        return await function(await self.awaitable).awaitable

    def flatten_future(self: Future[Future[T]]) -> Future[T]:
        return self.then_future(identity)

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


def wrap_future(function: Callable[P, Awaitable[T]]) -> Callable[P, Future[T]]:
    """Wraps an asynchronous `function` returning `T` into a function
    returning [`Future[T]`][wraps.future.Future].

    Example:
        ```python
        @wrap_future
        async def function() -> int:
            return 42

        string = "42"

        result = await function().map_future(str)

        assert result == string
        ```

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        return Future(function(*args, **kwargs))

    return wrap
