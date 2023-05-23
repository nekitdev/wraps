from typing import Awaitable, Callable, Generator, TypeVar

from attrs import define, field
from funcs.decorators import wraps
from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec, final

from wraps.option import Null, Option, Some

__all__ = ("ReAwaitable", "reawaitable")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)


@final
@define()
class ReAwaitable(Awaitable[T]):
    """Wraps awaitables to allow re-awaiting."""

    _awaitable: Awaitable[T] = field(repr=False)
    _option: Option[T] = field(factory=Null, repr=False, init=False)

    @property
    async def awaitable(self) -> T:
        option = self._option

        if option.is_null():
            self._option = option = Some(await self._awaitable)

        return option.unwrap()

    def __await__(self) -> Generator[None, None, T]:
        return self.awaitable.__await__()


ReAsyncCallable = Callable[P, ReAwaitable[T]]


def reawaitable(function: AsyncCallable[P, T]) -> ReAsyncCallable[P, T]:
    """Wraps the asynchronous `function` to allow re-awaiting.

    Example:
        Wrap the `function` to make it re-awaitable:

        ```python
        from wraps import reawaitable

        @reawaitable
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
