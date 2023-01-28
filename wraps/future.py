from __future__ import annotations

from functools import wraps
from typing import AsyncIterator, Awaitable, Callable, Generator, TypeVar

from attrs import define, field, frozen
from iters import AsyncIter, async_iter, async_next_unchecked
from typing_extensions import ParamSpec

from wraps.option import Null, Option, Some, is_null
from wraps.typing import AsyncUnary, Unary
from wraps.utils import async_identity, identity

__all__ = ("ReAwaitable", "Future", "wrap_future")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")


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
    awaitable: ReAwaitable[T] = field(repr=False, converter=ReAwaitable)

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
        return self.async_iter().unwrap()

    def async_iter(self) -> AsyncIter[T]:
        """Returns an asynchronous iterator over the result of this
        [`Future[T]`][wraps.future.Future].

        Returns:
            An asynchronous iterator over the result of the future.
        """
        return async_iter(self.actual_async_iter())

    async def actual_async_iter(self) -> AsyncIterator[T]:
        yield await self.awaitable

    @classmethod
    def do(cls, async_iterator: AsyncIterator[U]) -> Future[U]:
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

        Returns:
            The next value in the async iterator, wrapped in the future.
        """
        return cls.create(cls.actual_do(async_iterator))

    @classmethod
    async def actual_do(cls, async_iterator: AsyncIterator[U]) -> U:
        return await async_next_unchecked(async_iterator)

    @classmethod
    def from_value(cls, value: U) -> Future[U]:
        """Wraps `value` of type `U` into [`Future[U]`][wraps.future.Future].

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
        return cls.create(async_identity(value))


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
        return Future.create(function(*args, **kwargs))

    return wrap
