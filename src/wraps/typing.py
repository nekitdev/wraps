"""Various type aliases."""

from __future__ import annotations

from typing import Callable, TypeVar

from typing_aliases import AsyncCallable
from typing_extensions import ParamSpec

from wraps.either import Either
from wraps.option import Option
from wraps.result import Result

__all__ = (
    # option
    "OptionCallable",
    "OptionAsyncCallable",
    # result
    "ResultCallable",
    "ResultAsyncCallable",
    # either
    "EitherCallable",
    "EitherAsyncCallable",
)

P = ParamSpec("P")

T = TypeVar("T")
E = TypeVar("E")

L = TypeVar("L")
R = TypeVar("R")


OptionCallable = Callable[P, Option[T]]
"""Represents option callables `(**P) -> Option[T]`."""

OptionAsyncCallable = AsyncCallable[P, Option[T]]
"""Represents option async callables `async (**P) -> Option[T]`."""


ResultCallable = Callable[P, Result[T, E]]
"""Represents result callables `(**P) -> Result[T, E]`."""

ResultAsyncCallable = AsyncCallable[P, Result[T, E]]
"""Represents result async callables `async (**P) -> Result[T, E]`."""


EitherCallable = Callable[P, Either[L, R]]
"""Represents either callables `(**P) -> Either[L, R]`."""

EitherAsyncCallable = AsyncCallable[P, Either[L, R]]
"""Represents either async callables `async (**P) -> Either[L, R]`."""
