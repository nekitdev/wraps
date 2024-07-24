"""Asynchronous computation using futures."""

from __future__ import annotations

from typing import AsyncIterator, Awaitable, Generator, TypeVar

from attrs import field, frozen
from funcs.functions import asyncify, identity
from typing_aliases import AsyncUnary, Unary

from wraps.primitives.reawaitable import ReAwaitable

__all__ = ("Future",)

async_identity = asyncify(identity)


T = TypeVar("T", covariant=True)
U = TypeVar("U")


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
        """Creates a [`Future[U]`][wraps.futures.base.Future] from an [`Awaitable[U]`][typing.Awaitable].

        Arguments:
            awaitable: The awaitable to wrap.

        Returns:
            The future wrapping the given awaitable.
        """
        return cls(awaitable)  # type: ignore[arg-type, return-value]

    def map_result(self, function: Unary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.futures.base.Future] to a [`Future[U]`][wraps.futures.base.Future]
        by applying the `function` to its result.

        Arguments:
            function: The function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.actual_map_result(function))

    def map_result_await(self, function: AsyncUnary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.futures.base.Future] to a [`Future[U]`][wraps.futures.base.Future]
        by applying the asynchronous `function` to its result.

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.actual_map_result_await(function))

    async def actual_map_result(self, function: Unary[T, U]) -> U:
        return function(await self.awaitable)

    async def actual_map_result_await(self, function: AsyncUnary[T, U]) -> U:
        return await function(await self.awaitable)

    def then(self, function: FutureUnary[T, U]) -> Future[U]:
        """Chains computation by applying the `function` to the result, returning the resulting
        [`Future[U]`][wraps.futures.base.Future].

        Arguments:
            function: The future-returning function to apply.

        Returns:
            The resulting future.
        """
        return self.create(self.actual_then(function))

    async def actual_then(self, function: Unary[T, Future[U]]) -> U:
        return await function(await self.awaitable).awaitable

    def flatten_result(self: Future[Future[U]]) -> Future[U]:
        """Flattens a [`Future[Future[U]]`][wraps.futures.base.Future]
        to a [`Future[U]`][wraps.futures.base.Future].

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
        [`Future[T]`][wraps.futures.base.Future].

        Returns:
            An asynchronous iterator over the result of the future.
        """
        yield await self.awaitable

    @classmethod
    def from_value(cls, value: U) -> Future[U]:
        """Wraps the `value` of type `U` into a [`Future[U]`][wraps.futures.base.Future].

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

            future = Future.from_value(value)

            assert await future is value
            ```

        Arguments:
            value: The value to wrap.

        Returns:
            The future wrapping the given value.
        """
        return cls.create(async_identity(value))


from wraps.futures.typing import FutureUnary
