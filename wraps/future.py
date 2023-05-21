"""Asynchronous computation using futures."""

from __future__ import annotations

from typing import AsyncIterator, Awaitable, Generator, TypeVar

from attrs import field, frozen
from typing_aliases import AsyncUnary, Unary

from wraps.reawaitable import ReAwaitable
from wraps.utils import async_identity, identity

__all__ = ("Future",)

T = TypeVar("T", covariant=True)
U = TypeVar("U")


# NOTE: functions here are suffixed with `future` to avoid name clashes with derived types


def reawaitable_converter(awaitable: Awaitable[T]) -> ReAwaitable[T]:
    return ReAwaitable(awaitable)


@frozen()
class Future(Awaitable[T]):
    """Represents future computations."""

    reawaitable: ReAwaitable[T] = field(repr=False, converter=reawaitable_converter)

    @property
    def awaitable(self) -> Awaitable[T]:
        return self.reawaitable.awaitable

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    @classmethod
    def create(cls, awaitable: Awaitable[U]) -> Future[U]:
        """Creates a [`Future[U]`][wraps.future.Future] from an [`Awaitable[U]`][typing.Awaitable].

        Arguments:
            awaitable: The awaitable to wrap.

        Returns:
            The future wrapping the given awaitable.
        """
        return cls(awaitable)  # type: ignore

    def map_future(self, function: Unary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to a [`Future[U]`][wraps.future.Future]
        by applying the `function` to its result.

        Arguments:
            function: The function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.actual_map_future(function))

    def map_future_await(self, function: AsyncUnary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.future.Future] to a [`Future[U]`][wraps.future.Future]
        by applying the asynchronous `function` to its result.

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
        """Chains computation by applying the `function` to the result, returning the resulting
        [`Future[U]`][wraps.future.Future].

        Arguments:
            function: The future-returning function to apply.

        Returns:
            The resulting future.
        """
        return self.create(self.actual_then(function))

    async def actual_then(self, function: Unary[T, Future[U]]) -> U:
        return await function(await self.awaitable).awaitable

    def flatten_future(self: Future[Future[T]]) -> Future[T]:
        """Flattens a [`Future[Future[T]]`][wraps.future.Future]
        to a [`Future[T]`][wraps.future.Future].

        This is identical to:

        ```python
        future.then(identity)
        ```

        Returns:
            The flattened future.
        """
        return self.then(identity)

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

        future = Future.create(async_identity(value))
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
