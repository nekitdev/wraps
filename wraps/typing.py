from typing import Callable, TypeVar

from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec

from wraps.option import Option
from wraps.result import Result

__all__ = (
    "OptionCallable",
    "OptionAsyncCallable",
    "ResultCallable",
    "ResultAsyncCallable",
)

P = ParamSpec("P")

T = TypeVar("T")
E = TypeVar("E")

OptionCallable = Callable[P, Option[T]]
OptionAsyncCallable = AsyncCallable[P, Option[T]]

ResultCallable = Callable[P, Result[T, E]]
ResultAsyncCallable = AsyncCallable[P, Result[T, E]]
