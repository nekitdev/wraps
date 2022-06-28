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
    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return function(*args, **kwargs)

        except OptionShortcut:
            return Null()

    return wrap


def result_shortcut(function: Callable[P, Result[T, E]]) -> Callable[P, Result[T, E]]:
    @wraps(function)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
        try:
            return function(*args, **kwargs)

        except ResultShortcut[E] as shortcut:
            return Error(shortcut.error)

    return wrap
