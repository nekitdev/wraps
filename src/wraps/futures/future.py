"""Asynchronous computation using futures."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Awaitable, Generator, TypeVar

from attrs import field, frozen
from funcs.decorators import wraps
from funcs.functions import asyncify, identity
from typing_aliases import AsyncCallable, AsyncUnary, Unary
from typing_extensions import ParamSpec

from wraps.futures.reawaitable import ReAwaitable
from wraps.reprs import empty_repr

if TYPE_CHECKING:
    from wraps.futures.typing import FutureCallable, FutureUnary

__all__ = ("Future", "future_value", "wrap_future")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")


@frozen()
class Future(Awaitable[T]):
    """Represents future computations."""

    awaitable: ReAwaitable[T] = field(converter=ReAwaitable)

    def __repr__(self) -> str:
        return empty_repr(self)

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    @classmethod
    def create(cls, awaitable: Awaitable[U]) -> Future[U]:
        """Creates a [`Future[U]`][wraps.futures.future.Future]
        from an [`Awaitable[U]`][typing.Awaitable].

        Arguments:
            awaitable: The awaitable to wrap.

        Returns:
            The future wrapping the given awaitable.
        """
        return cls(awaitable)  # type: ignore[arg-type, return-value]

    def future_map(self, function: Unary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.futures.future.Future] to a [`Future[U]`][wraps.futures.future.Future]
        by applying the `function` to its result.

        Arguments:
            function: The function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.raw_future_map(function))

    def future_map_await(self, function: AsyncUnary[T, U]) -> Future[U]:
        """Maps a [`Future[T]`][wraps.futures.future.Future]
        to a [`Future[U]`][wraps.futures.future.Future]
        by applying the asynchronous `function` to its result.

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped future.
        """
        return self.create(self.raw_future_map_await(function))

    async def raw_future_map(self, function: Unary[T, U]) -> U:
        return function(await self.awaitable)

    async def raw_future_map_await(self, function: AsyncUnary[T, U]) -> U:
        return await function(await self.awaitable)

    def then(self, function: FutureUnary[T, U]) -> Future[U]:
        """Chains computation by applying the `function` to the result, returning the resulting
        [`Future[U]`][wraps.futures.future.Future].

        Arguments:
            function: The future-returning function to apply.

        Returns:
            The resulting future.
        """
        return self.create(self.raw_then(function))

    async def raw_then(self, function: FutureUnary[T, U]) -> U:
        return await function(await self.awaitable).awaitable

    def future_flatten(self: Future[Future[U]]) -> Future[U]:
        """Flattens a [`Future[Future[U]]`][wraps.futures.future.Future]
        to a [`Future[U]`][wraps.futures.future.Future].

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
        """Creates an asynchronous iterator yielding the result of this
        [`Future[T]`][wraps.futures.future.Future].

        Returns:
            An asynchronous iterator yielding the result of the future.
        """
        yield await self.awaitable

    @classmethod
    def from_value(cls, value: U) -> Future[U]:
        """Wraps the `value` of type `U` into a [`Future[U]`][wraps.futures.future.Future].

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


async_identity = asyncify(identity)

future_value = Future.from_value
"""An alias of [`Future.from_value`][wraps.futures.future.Future.from_value]."""


def wrap_future(function: AsyncCallable[P, T]) -> FutureCallable[P, T]:
    """Wraps the asynchronous `function` returning `T` into the function
    returning [`Future[T]`][wraps.futures.future.Future].

    Example:
        ```python
        @wrap_future
        async def function() -> int:
            return 42

        string = "42"

        result = await function().future_map(str)

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
