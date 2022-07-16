from functools import wraps
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

from wraps.errors import OptionShortcut, ResultShortcut
from wraps.option import Null, Option
from wraps.result import Error, Result

__all__ = ("option_shortcut", "result_shortcut")

P = ParamSpec("P")

T = TypeVar("T")

E = TypeVar("E")


def option_shortcut(function: Callable[P, Option[T]]) -> Callable[P, Option[T]]:
    """Decorates the `function` returning [`Option[T]`][wraps.result.Option]
    to handle *early returns* via `Q` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return function(*args, **kwargs)

        except OptionShortcut:
            return Null()

    return wrap


def result_shortcut(function: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
    """Decorates the `function` returning [`Result[T, E]`][wraps.result.Result]
    to handle *early returns* via `Q` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return function(*args, **kwargs)

        except ResultShortcut[E] as shortcut:
            return Error(shortcut.error)

    return wrap
