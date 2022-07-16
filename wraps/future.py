from __future__ import annotations

from typing import AsyncIterator, Awaitable, Callable, Generator, TypeVar

from attrs import define, field, frozen
from typing_extensions import ParamSpec

from wraps.option import Null, Option, Some, is_null
from wraps.typing import Unary

__all__ = ("Future", "wrap_future")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")


async def async_identity(value: V) -> V:
    return value


@define()
class ReAwaitable(Awaitable[T]):
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

    def map(self, function: Unary[T, U]) -> Future[U]:
        return type(self)(self.actual_map(function))  # type: ignore

    def map_await(self, function: Unary[T, Awaitable[U]]) -> Future[U]:
        return type(self)(self.actual_map_await(function))  # type: ignore

    async def actual_map(self, function: Unary[T, U]) -> U:
        return function(await self.awaitable)

    async def actual_map_await(self, function: Unary[T, Awaitable[U]]) -> U:
        return await function(await self.awaitable)

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    async def async_iter(self) -> AsyncIterator[T]:
        yield await self.awaitable

    @classmethod
    def do(cls, async_iterator: AsyncIterator[T]) -> Future[T]:
        return cls(cls.actual_do(async_iterator))

    @classmethod
    async def actual_do(cls, async_iterator: AsyncIterator[T]) -> T:
        return await async_iterator.__anext__()

    @classmethod
    def from_value(cls, value: T) -> Future[T]:  # type: ignore
        return cls(async_identity(value))


def wrap_future(function: Callable[P, Awaitable[T]]) -> Callable[P, Future[T]]:
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Future[T]:
        return Future(function(*args, **kwargs))

    return wrap
