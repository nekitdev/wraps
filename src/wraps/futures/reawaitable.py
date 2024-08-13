from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Generator, TypeVar, final

from attrs import define, field
from funcs.decorators import wraps
from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec

from wraps.option import NULL, Option, Some
from wraps.reprs import empty_repr

if TYPE_CHECKING:
    from wraps.futures.typing import ReAsyncCallable

__all__ = ("ReAwaitable", "wrap_reawaitable")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)


@final
@define()
class ReAwaitable(Awaitable[T]):
    """Wraps the given awaitable to allow re-awaiting."""

    _awaitable: Awaitable[T] = field()
    _result: Option[T] = field(default=NULL, init=False)

    def __repr__(self) -> str:
        return empty_repr(self)

    def __await__(self) -> Generator[None, None, T]:
        return self.execute().__await__()

    async def execute(self) -> T:
        """Returns the cached result or executes the contained awaitable and caches its result.

        Returns:
            The execution result.
        """
        result = self._result

        if result.is_null():
            value = await self._awaitable

            self._result = Some(value)

            return value

        return result.unwrap()

    @property
    def result(self) -> Option[T]:
        """The cached result."""
        return self._result


def wrap_reawaitable(function: AsyncCallable[P, T]) -> ReAsyncCallable[P, T]:
    """Wraps the asynchronous `function` to allow re-awaiting.

    Example:
        Wrap the `function` to make it re-awaitable:

        ```python
        @wrap_reawaitable
        async def function() -> int:
            return 42
        ```

        Now the `function` can be re-awaited:

        ```python
        >>> awaitable = function()
        >>> await awaitable
        42
        >>> await awaitable
        42
        >>> await awaitable
        42
        >>> # ad infinitum...
        ```

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> ReAwaitable[T]:
        return ReAwaitable(function(*args, **kwargs))

    return wrap
