from typing import Awaitable, Generator, TypeVar, final

from attrs import define, field

from wraps.primitives.option import NULL, Option, Some

__all__ = ("ReAwaitable",)

T = TypeVar("T", covariant=True)


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
