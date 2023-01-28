from typing import TypeVar

__all__ = ("async_identity", "identity")

T = TypeVar("T")


async def async_identity(item: T) -> T:
    return item


def identity(item: T) -> T:
    return item
