from __future__ import annotations

from typing import Callable, Generic, Type, TypeVar, final

from attrs import frozen
from funcs.decorators import wraps
from typing_aliases import AnyError, AsyncCallable, NormalError
from typing_extensions import ParamSpec

from wraps.primitives.result import Error, Ok, Result
from wraps.primitives.typing import ResultAsyncCallable, ResultCallable

__all__ = ("WrapResult", "WrapResultAwait", "wrap_result", "wrap_result_await")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)

E = TypeVar("E", bound=AnyError)
F = TypeVar("F", bound=AnyError)


@final
@frozen()
class WrapResult(Generic[E]):
    """Wraps functions returning `T` into functions returning
    [`Result[T, E]`][wraps.primitives.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.primitives.result.Error] on `error`
    of [`error_type`][wraps.wraps.result.WrapResult.error_type], wrapping the resulting `value`
    into [`Ok(value)`][wraps.primitives.result.Ok].

    Example:
        ```python
        wrap_value_error = WrapResult(ValueError)

        @wrap_value_error
        def parse(string: str) -> int:
            return int(string)

        assert parse("256").is_ok()
        assert parse("uwu").is_error()
        ```
    """

    error_type: Type[E]
    """The error type to handle."""

    @classmethod
    def create(cls, error_type: Type[F]) -> WrapResult[F]:
        return cls(error_type)  # type: ignore[arg-type, return-value]

    def __call__(self, function: Callable[P, T]) -> ResultCallable[P, T, E]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[F]) -> WrapResult[F]:
        return self.create(error_type)


wrap_result = WrapResult(NormalError)
"""An instance of [`WrapResult[NormalError]`][wraps.wraps.result.WrapResult]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapResultAwait(Generic[E]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Result[T, ET]`][wraps.primitives.result.Result].

    Errors are handled via returning [`Error(error)`][wraps.primitives.result.Error] on `error`
    of `error_type`, wrapping the resulting `value` into [`Ok(value)`][wraps.primitives.result.Ok].

    Example:
        ```python
        wrap_value_error_await = WrapResultAwait(ValueError)

        @wrap_value_error_await
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_ok()
        assert (await parse("uwu")).is_error()
        ```
    """

    error_type: Type[E]
    """The error type to handle."""

    @classmethod
    def create(cls, error_type: Type[F]) -> WrapResultAwait[F]:
        return cls(error_type)  # type: ignore[arg-type, return-value]

    def __call__(self, function: AsyncCallable[P, T]) -> ResultAsyncCallable[P, T, E]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, E]:
            try:
                return Ok(await function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[F]) -> WrapResultAwait[F]:
        return self.create(error_type)


wrap_result_await = WrapResultAwait(NormalError)
"""An instance of [`WrapResultAwait[NormalError]`][wraps.wraps.result.WrapResultAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""
