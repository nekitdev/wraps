from typing import Protocol, runtime_checkable

from typing_aliases import required

__all__ = ("ToString", "to_string", "to_short_string")


@runtime_checkable
class ToString(Protocol):
    @required
    def to_string(self) -> str: ...

    def to_short_string(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()


def to_string(item: ToString) -> str:
    return item.to_string()


def to_short_string(item: ToString) -> str:
    return item.to_short_string()
