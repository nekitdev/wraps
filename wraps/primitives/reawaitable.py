from typing import Awaitable, Generator, TypeVar, final

from attrs import define, field
from named import get_type_name
from typing_extensions import ParamSpec

from wraps.primitives.option import NULL, Option, Some

__all__ = ("ReAwaitable",)

P = ParamSpec("P")
R = TypeVar("R")

T = TypeVar("T", covariant=True)

REPRESENTATION = "<{} ({})>"
representation = REPRESENTATION.format

PENDING = "pending"
READY = "ready: {}"
ready = READY.format


@final
@define()
class ReAwaitable(Awaitable[T]):
    """Wraps awaitables to allow re-awaiting."""

    _awaitable: Awaitable[T] = field(repr=False)
    _result: Option[T] = field(default=NULL, repr=False, init=False)

    @property
    async def awaitable(self) -> T:
        result = self._result

        if result.is_null():
            value = await self._awaitable

            self._result = result = Some(value)

        return result.unwrap()

    @property
    def result(self) -> Option[T]:
        return self._result

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()

    def __repr__(self) -> str:
        return representation(get_type_name(self), self.result.map_or(PENDING, ready))
