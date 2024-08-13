from __future__ import annotations

from typing import AsyncIterator, Iterator, TypeVar

from typing_extensions import Never

__all__ = ("async_empty", "async_once", "empty", "once")

# NOTE: we can not use `iters` as it depends on `wraps` heavily

T = TypeVar("T")


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
