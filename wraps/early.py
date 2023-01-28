from functools import wraps
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

from wraps.errors import EarlyOption, EarlyResult
from wraps.option import Null, Option
from wraps.result import Error, Result

__all__ = ("early_option", "early_result")

P = ParamSpec("P")

T = TypeVar("T")

E = TypeVar("E")


def early_option(function: Callable[P, Option[T]]) -> Callable[P, Option[T]]:
    """Decorates the `function` returning [`Option[T]`][wraps.result.Option]
    to handle *early returns* via `early` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return function(*args, **kwargs)

        except EarlyOption:
            return Null()

    return wrap


def early_result(function: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
    """Decorates the `function` returning [`Result[T, E]`][wraps.result.Result]
    to handle *early returns* via `early` (`?` in Rust) operator.

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return function(*args, **kwargs)

        except EarlyResult[E] as early:
            return Error(early.error)

    return wrap
