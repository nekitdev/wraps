from typing import AsyncIterator, Iterator, TypeVar

from typing_extensions import Never

__all__ = (
    "async_identity",
    "async_empty",
    "async_once",
    "identity",
    "empty",
    "once",
)

# NOTE: we can not use `iters` here as it depends on `wraps`

T = TypeVar("T")


async def async_identity(item: T) -> T:
    return item


def identity(item: T) -> T:
    return item


async def async_empty() -> AsyncIterator[Never]:
    return
    yield


def empty() -> Iterator[Never]:
    return
    yield


async def async_once(item: T) -> AsyncIterator[T]:
    yield item


def once(item: T) -> Iterator[T]:
    yield item
