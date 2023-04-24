from __future__ import annotations

from typing import AsyncIterator, Awaitable, Generator, TypeVar

from attrs import define, field
from funcs.typing import AsyncUnary, Unary

from wraps.reawaitable import ReAwaitable
from wraps.utils import async_identity, identity

__all__ = ("Future",)

T = TypeVar("T", covariant=True)
U = TypeVar("U")

# NOTE: functions here are suffixed with `future` to avoid name clashes with derived types


@define()
class Future(Awaitable[T]):
    reawaitable: ReAwaitable[T] = field(repr=False)

    @property
    def awaitable(self) -> Awaitable[T]:
        return self.reawaitable.awaitable

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    @classmethod
    def from_awaitable(cls, awaitable: Awaitable[U]) -> Future[U]:
        """Creates a [`Future[U]`][wraps.future.Future] from an [`Awaitable[U]`][typing.Awaitable].

        Arguments:
            awaitable: The awaitable to wrap.

        Returns:
            The future wrapping the given awaitable.
        """
        return cls(ReAwaitable(awaitable))  # type: ignore

    def map_future(self, function: Unary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to a [`Future[U]`][wraps.future.Future]
        by applying the `function` to the result.

        Arguments:
            function: The function to apply.

        Returns:
            The mapped future.
        """
        return self.from_awaitable(self.actual_map_future(function))

    def map_future_await(self, function: AsyncUnary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to a [`Future[U]`][wraps.future.Future]
        by applying the asynchronous `function` to the result.

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped future.
        """
        return self.from_awaitable(self.actual_map_future_await(function))

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
        return self.from_awaitable(self.actual_then_future(function))

    async def actual_then_future(self, function: Unary[T, Future[U]]) -> U:
        return await function(await self.awaitable).awaitable

    def flatten_future(self: Future[Future[T]]) -> Future[T]:
        return self.then_future(identity)

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    async def async_iter(self) -> AsyncIterator[T]:
        """Creates an asynchronous iterator over the result of this
        [`Future[T]`][wraps.future.Future].

        Returns:
            An asynchronous iterator over the result of the future.
        """
        yield await self.awaitable

    @classmethod
    def from_value(cls, value: U) -> Future[U]:
        """Wraps the `value` of type `U` into a [`Future[U]`][wraps.future.Future].

        This is functionally the same as:

        ```python
        async def async_identity(value: T) -> T:
            return value

        value = 42

        future = Future.from_awaitable(async_identity(value))
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
        return cls.from_awaitable(async_identity(value))
