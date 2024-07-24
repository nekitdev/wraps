from typing import TypeVar

from funcs.decorators import wraps
from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec

from wraps.primitives.reawaitable import ReAwaitable
from wraps.primitives.typing import ReAwaitableCallable

__all__ = ("wrap_reawaitable",)

P = ParamSpec("P")

R = TypeVar("R")


def wrap_reawaitable(function: AsyncCallable[P, R]) -> ReAwaitableCallable[P, R]:
    """Wraps the asynchronous `function` to allow re-awaiting.

    Example:
        Wrap the `function` to make it re-awaitable:

        ```python
        from wraps import wrap_reawaitable

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
    def wrap(*args: P.args, **kwargs: P.kwargs) -> ReAwaitable[R]:
        return ReAwaitable(function(*args, **kwargs))

    return wrap
