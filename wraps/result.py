"""Error handling with the [`Result[T, E]`][wraps.result.Result] type.

[`Result[T, E]`][wraps.result.Result] is the type used for returning and propagating errors.

It is an enum with the variants, [`Ok[T]`][wraps.result.Ok],
representing success and containing a value,
and [`Error[E]`][wraps.result.Error], representing error and containing an error value.

Functions return [`Result[T, E]`][wraps.result.Result] whenever errors are expected and recoverable.

For instance, our `divide` function from the [`option`][wraps.option] section:

```python
# result.py

from enum import Enum

from wraps import Error, Ok, Result


class DivideError(Enum):
    DIVISION_BY_ZERO = "division by zero"


def divide(numerator: float, denominator: float) -> Result[float, DivideError]:
    return Ok(numerator / denominator) if denominator else Error(DivideError.DIVISION_BY_ZERO)
```

```python
from wraps import Error, Ok

from result import divide

result = divide(1.0, 2.0)

match result:
    case Ok(value):
        print(value)

    case Error(error):
        print(error)
```
"""

from __future__ import annotations

from abc import abstractmethod as required
from typing import AsyncIterable, AsyncIterator, Iterable, Iterator, TypeVar, Union

from attrs import frozen
from typing_aliases import (
    AnyError,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)
from typing_extensions import Literal, Never, ParamSpec, Protocol, TypeGuard, final

from wraps.errors import EarlyResult, panic
from wraps.option import Null, Option, Some
from wraps.utils import async_empty, async_once, empty, identity, once

__all__ = ("Result", "Ok", "Error", "is_ok", "is_error")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")

V = TypeVar("V")


class ResultProtocol(AsyncIterable[T], Iterable[T], Protocol[T, E]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter()

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    @required
    def is_ok(self) -> bool:
        """Checks if the result is [`Ok[T]`][wraps.result.Ok].

        Example:
            ```python
            ok = Ok(42)
            assert ok.is_ok()

            error = Error(13)
            assert not error.is_ok()
            ```

        Returns:
            Whether the result is [`Ok[T]`][wraps.result.Ok].
        """
        ...

    @required
    def is_ok_and(self, predicate: Predicate[T]) -> bool:
        """Checks if the result is [`Ok[T]`][wraps.result.Ok] and the value
        inside of it matches the `predicate`.

        Example:
            ```python
            def is_positive(value: int) -> bool:
                return value > 0

            ok = Ok(13)
            assert ok.is_ok_and(is_positive)

            zero = Ok(0)
            assert not zero.is_ok_and(is_positive)

            error = Error(7)
            assert not error.is_ok_and(is_positive)
            ```

        Arguments:
            predicate: The predicate to check the contained value against.

        Returns:
            Whether the result is [`Ok[T]`][wraps.result.Ok] and the predicate is matched.
        """
        ...

    @required
    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        """Checks if the result is [`Ok[T]`][wraps.result.Ok] and the value
        inside of it matches the asynchronous `predicate`.

        Example:
            ```python
            async def is_positive(value: int) -> bool:
                return value > 0

            ok = Ok(13)
            assert await ok.is_ok_and_await(is_positive)

            zero = Ok(0)
            assert not await zero.is_ok_and_await(is_positive)

            error = Error(7)
            assert not await error.is_ok_and_await(is_positive)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

        Returns:
            Whether the result is [`Ok[T]`][wraps.result.Ok] and
            the asynchronous predicate is matched.
        """
        ...

    @required
    def is_error(self) -> bool:
        """Checks if the result is [`Error[E]`][wraps.result.Error].

        Example:
            ```python
            error = Error(34)
            assert error.is_error()

            ok = Ok(69)
            assert not ok.is_error()
            ```

        Returns:
            Whether the result is [`Error[E]`][wraps.result.Error].
        """
        ...

    @required
    def is_error_and(self, predicate: Predicate[E]) -> bool:
        """Checks if the result is [`Error[E]`][wraps.result.Error] and the value
        inside of it matches the `predicate`.

        Example:
            ```python
            def is_negative(value: int) -> bool:
                return value < 0

            error = Error(-13)
            assert error.is_error_and(is_positive)

            zero = Error(0)
            assert not zero.is_error_and(is_positive)

            ok = Ok(7)
            assert not ok.is_error_and(is_positive)
            ```

        Arguments:
            predicate: The predicate to check the contained value against.

        Returns:
            Whether the result is [`Error[E]`][wraps.result.Error] and the predicate is matched.
        """
        ...

    @required
    async def is_error_and_await(self, predicate: AsyncPredicate[E]) -> bool:
        """Checks if the result is [`Error[E]`][wraps.result.Error] and the value
        inside of it matches the asynchronous `predicate`.

        Example:
            ```python
            async def is_negative(value: int) -> bool:
                return value < 0

            error = Error(-13)
            assert await error.is_error_and_await(is_negative)

            zero = Error(0)
            assert not await zero.is_error_and_await(is_negative)

            ok = Ok(7)
            assert not await ok.is_error_and_await(is_negative)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

        Returns:
            Whether the result is [`Error[E]`][wraps.result.Error] and
            the asynchronous predicate is matched.
        """
        ...

    @required
    def expect(self, message: str) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> ok.expect("error!")
            42
            >>> error = Error(0)
            >>> error.expect("error!")
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: error!
            ```

        Arguments:
            message: The message used in panicking.

        Raises:
            Panic: Panics with the `message` if the result is [`Error[E]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    @required
    def expect_error(self, message: str) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> ok.expect_error("ok!")
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: ok!

            >>> error = Error(0)
            >>> error.expect_error("ok!")
            0
            ```

        Arguments:
            message: The message used in panicking.

        Raises:
            Panic: Panics with the `message` if the result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap(self) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`).

        Because this function may panic, its use is generally discouraged.

        Instead, prefer to use pattern matching and handle the [`Error[E]`][wraps.result.Error]
        case explicitly, or call [`unwrap_or`][wraps.result.ResultProtocol.unwrap_or]
        or [`unwrap_or_else`][wraps.result.ResultProtocol.unwrap_or_else].

        Example:
            ```python
            >>> ok = Ok(13)
            >>> ok.unwrap()
            13

            >>> error = Error(0)
            >>> error.unwrap()
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: called `unwrap` on error
            ```

        Raises:
            Panic: Panics if the result is [`Error[E]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap_or(self, default: T) -> T:  # type: ignore
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value or the provided `default`.

        Example:
            ```python
            ok = Ok(69)
            assert ok.unwrap_or(0)

            error = Error(13)
            assert not error.unwrap_or(0)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained value or the `default` one.
        """
        ...

    @required
    def unwrap_or_else(self, default: Nullary[T]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or computes it from the `default` function.

        Example:
            ```python
            ok = Ok(5)
            assert ok.unwrap_or_else(int)

            error = Error(8)
            assert not error.unwrap_or_else(int)
            ```

        Arguments:
            default: The default-computing function to use.

        Returns:
            The contained value or the `default()` one.
        """
        ...

    @required
    async def unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or computes it from the asynchronous `default` function.

        Example:
            ```python
            async def default() -> int:
                return 0

            ok = Ok(5)
            assert await ok.unwrap_or_else_await(default)

            error = Error(8)
            assert not await error.unwrap_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default-computing function to use.

        Returns:
            The contained value or the `await default()` one.
        """
        ...

    @required
    def unwrap_error(self) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value.

        Because this function may panic, its use is generally discouraged.

        Instead, prefer to use pattern matching and handle the [`Ok[T]`][wraps.result.Ok]
        case explicitly, or call [`unwrap_error_or`][wraps.result.ResultProtocol.unwrap_error_or]
        or [`unwrap_error_or_else`][wraps.result.ResultProtocol.unwrap_error_or_else].

        Example:
            ```python
            >>> error = Error(13)
            >>> error.unwrap_error()
            13

            >>> ok = Ok(42)
            >>> ok.unwrap_error()
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: called `unwrap_error` on ok
            ```

        Raises:
            Panic: Panics if the result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained error value.
        """
        ...

    @required
    def unwrap_error_or(self, default: E) -> E:  # type: ignore
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`)
        or a provided default.

        Example:
            ```python
            error = Error(1)
            assert error.unwrap_error_or(0)

            ok = Ok(2)
            assert not ok.unwrap_error_or(0)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained error value or the `default` one.
        """
        ...

    @required
    def unwrap_error_or_else(self, default: Nullary[E]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value
        or computes it from the `default` function.

        Example:
            ```python
            error = Error(5)
            assert error.unwrap_error_or_else(int)

            ok = Ok(8)
            assert not ok.unwrap_error_or_else(int)

        Arguments:
            default: The default-computing function to use.

        Returns:
            The contained error value or the `default()` one.
        """
        ...

    @required
    async def unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value
        or computes it from the asynchronous `default` function.

        Example:
            ```python
            async def default() -> int:
                return 0

            error = Error(13)
            assert await error.unwrap_error_or_else_await(default)

            ok = Ok(5)
            assert not await ok.unwrap_error_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default-computing function to use.

        Returns:
            The contained error value or the `await default()` one.
        """
        ...

    @required
    def raising(self: ResultProtocol[T, AnyError]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value or raises the
        contained [`Error[AnyError]`][wraps.result.Error] value.

        Example:
            ```python
            >>> ok = Ok(13)
            >>> ok.raising()
            13

            >>> error = Error(ValueError("error..."))
            >>> error.raising()
            Traceback (most recent call last):
              ...
            ValueError: error...
            ```

        Raises:
            AnyError: The contained error, if the result is [`Error[AnyError]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    @required
    def ok(self) -> Option[T]:
        """Converts a [`Result[T, E]`][wraps.result.Result]
        into an [`Option[T]`][wraps.option.Option].

        Converts `self` into an [`Option[T]`][wraps.option.Option], discarding errors, if any.

        Example:
            ```python
            ok = Ok(42)

            assert ok.ok().is_some()

            error = Error(0)

            assert error.ok().is_null()
            ```

        Returns:
            The converted option.
        """
        ...

    @required
    def error(self) -> Option[E]:
        """Converts a [`Result[T, E]`][wraps.result.Result]
        into an [`Option[E]`][wraps.option.Option].

        Converts `self` into an [`Option[E]`][wraps.option.Option],
        discarding success values, if any.

        Example:
            ```python
            error = Error(13)

            assert error.error().is_some()

            ok = Ok(2)

            assert ok.error().is_null()
            ```

        Returns:
            The converted option.
        """
        ...

    @required
    def inspect(self, function: Inspect[T]) -> Result[T, E]:
        """Inspects a possibly contained [`Ok[T]`][wraps.result.Ok] value.

        Example:
            ```python
            ok = Ok("Hello, world!")

            same = ok.inspect(print)  # Hello, world!

            assert ok == same
            ```

        Arguments:
            function: The inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @required
    async def inspect_await(self, function: AsyncInspect[T]) -> Result[T, E]:
        """Inspects a possibly contained [`Ok[T]`][wraps.result.Ok] value.

        Example:
            ```python
            async def function(value: str) -> None:
                print(value)

            ok = Ok("Hello, world!")

            same = await ok.inspect_await(function)  # Hello, world!

            assert ok == same
            ```

        Arguments:
            function: The asynchronous inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @required
    def inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        """Inspects a possibly contained [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            error = Error("Bye, world!")

            same = error.inspect_error(print)  # Bye, world!

            assert error == same
            ```

        Arguments:
            function: The error-inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @required
    async def inspect_error_await(self, function: AsyncInspect[E]) -> Result[T, E]:
        """Inspects a possibly contained [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            async def function(value: str) -> None:
                print(value)

            error = Error("Bye, world!")

            same = await error.inspect_error_await(function)  # Bye, world!

            assert error == same
            ```

        Arguments:
            function: The asynchronous error-inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @required
    def map(self, function: Unary[T, U]) -> Result[U, E]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[U, E]`][wraps.result.Result]
        by applying `function` to the contained [`Ok[T]`][wraps.result.Ok] value,
        leaving any [`Error[E]`][wraps.result.Error] values untouched.

        This function can be used to compose the results of two functions.

        Example:
            ```python
            value = 69
            mapped = "69"

            ok = Ok(value)

            assert ok.map(str) == Ok(mapped)

            error = Error(0)

            assert error.map(str) == error
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        """Returns the default value (if errored), or applies the `function`
        to the contained value (if succeeded).

        Example:
            ```python
            ok = Ok("Hello, world!")
            print(ok.map_or(42, len))  # 13

            error = Error("error...")
            print(error.map_or(42, len))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if errored), or applies the `function`
        to the contained value (if succeeded).

        Example:
            ```python
            ok = Ok("Hello, world!")
            print(ok.map_or_else(int, len))  # 13

            error = Error("error!")
            print(error.map_or_else(int, len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if errored), or applies the `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def default() -> int:
                return 0

            ok = Ok("Hello, world!")
            print(await ok.map_or_else_await(default, len))  # 13

            error = Error("error!")
            print(await error.map_or_else_await(default, len))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    def map_error(self, function: Unary[E, F]) -> Result[T, F]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[T, F]`][wraps.result.Result]
        by applying the `function` to the contained [`Error[E]`][wraps.result.Error] value,
        leaving any [`Ok[T]`][wraps.result.Ok] values untouched.

        Example:
            ```python
            value = 42
            mapped = "42"

            error = Error(value)

            assert error.map_error(str) == Error(mapped)

            ok = Ok(2)

            assert ok.map_error(str) == ok
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    def map_error_or(self, default: F, function: Unary[E, F]) -> F:
        """Returns the default value (if succeeded), or applies the `function`
        to the contained error value (if errored).

        Example:
            ```python
            error = Error("nekit")
            print(error.map_error_or(13, len))  # 5

            ok = Ok("ok")
            print(error.map_error_or(13, len))  # 13
            ```

        Arguments:
            default: The default value to use.
            function: The function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the `function`
        to the contained value (if errored).

        Example:
            ```python
            error = Error("error...")
            print(error.map_error_or_else(int, len))  # 8

            ok = Ok("ok!")
            print(ok.map_error_or_else(int, len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the `function`
        to the contained value (if errored).

        Example:
            ```python
            error = Error("error...")
            print(await error.map_error_or_else(int, len))  # 8

            ok = Ok("ok!")
            print(await ok.map_error_or_else(int, len))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_await(self, function: AsyncUnary[T, U]) -> Result[U, E]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[U, E]`][wraps.result.Result]
        by applying the asynchronous `function` to the contained [`Ok[T]`][wraps.result.Ok] value,
        leaving any [`Error[E]`][wraps.result.Error] values untouched.

        This function can be used to compose the results of two functions.

        Example:
            ```python
            async def function(value: int) -> str:
                return str(value)

            value = 69
            mapped = "69"

            ok = Ok(value)

            assert await ok.map_await(function) == Ok(mapped)

            error = Error(0)

            assert await error.map_await(function) == error
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        """Returns the default value (if errored), or applies the asynchronous `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            ok = Ok("Hello, world!")
            print(await ok.map_await_or(42, function))  # 13

            error = Error("error...")
            print(error.map_await_or(42, function))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        """Computes the default value (if errored), or applies the asynchronous `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            ok = Ok("Hello, world!")
            print(await ok.map_await_or_else(int, async_len))  # 13

            error = Error("error!")
            print(await error.map_await_or_else(int, async_len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        """Computes the default value (if errored), or applies the asynchronous `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def default() -> int:
                return 0

            async def function(value: str) -> int:
                return len(value)

            ok = Ok("Hello, world!")
            print(await ok.map_await_or_else_await(default, function))  # 13

            error = Error("error!")
            print(await error.map_await_or_else_await(default, function))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_error_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[T, F]`][wraps.result.Result]
        by applying the asynchronous `function` to the contained [`Error[E]`][wraps.result.Error]
        value, leaving any [`Ok[T]`][wraps.result.Ok] values untouched.

        Example:
            ```python
            async def function(value: int) -> str:
                return str(value)

            value = 42
            mapped = "42"

            error = Error(value)

            assert await error.map_error_await(function) == Error(mapped)

            ok = Ok(13)

            assert await ok.map_error_await(function) == ok
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    async def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        """Returns the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            error = Error("Bye, world!")
            print(await error.map_error_await_or(42, function))  # 11

            ok = Ok("Hello, world!")
            print(await ok.map_error_await_or(42, function))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    async def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            error = Error("Bye, world!")
            print(await error.map_error_await_or_else(int, async_len))  # 11

            ok = Ok("Hello, world!")
            print(await ok.map_error_await_or_else(int, async_len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        """Computes the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def default() -> int:
                return 0

            async def function(value: str) -> int:
                return len(value)

            error = Error("error")
            print(await error.map_error_await_or_else_await(default, function))  # 5

            ok = Ok("ok")
            print(await ok.map_error_await_or_else_await(default, function))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    def iter(self) -> Iterator[T]:
        """Returns an iterator over the possibly contained value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> next(ok.iter(), 0)
            42
            >>> error = Error(13)
            >>> next(error.iter(), 0)
            0
            ```

        Returns:
            An iterator over the possibly contained value.
        """
        ...

    @required
    def iter_error(self) -> Iterator[E]:
        """Returns an iterator over the possibly contained error value.

        Example:
            ```python
            >>> error = Error(13)
            >>> next(error.iter_error(), 0)
            13
            >>> ok = Ok(1)
            >>> next(ok.iter_error(), 0)
            0
            ```

        Returns:
            An iterator over the possibly contained error value.
        """
        ...

    @required
    def async_iter(self) -> AsyncIterator[T]:
        """Returns an asynchronous iterator over the possibly contained
        [`Ok[T]`][wraps.result.Ok] value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> await async_next(ok.async_iter(), 0)
            42
            >>> error = Error(13)
            >>> await async_next(error.async_iter(), 0)
            0
            ```

        Returns:
            An asynchronous iterator over the possibly contained value.
        """
        ...

    @required
    def async_iter_error(self) -> AsyncIterator[E]:
        """Returns an asynchronous iterator over the possibly contained
        [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            >>> error = Error(42)
            >>> await async_next(error.async_iter_error(), 0)
            42
            >>> ok = Ok(13)
            >>> await async_next(ok.async_iter_error(), 0)
            0
            ```

        Returns:
            An asynchronous iterator over the possibly contained error value.
        """
        ...

    @required
    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        """Returns the result if it is an [`Error[E]`][wraps.result.Error],
        otherwise calls the `function` with the wrapped value and returns the result.

        This function is also known as *bind* in functional programming.

        Example:
            ```python
            class InverseError(Enum):
                DIVISION_BY_ZERO = "division by zero"

            def inverse(value: float) -> Result[float, InverseError]:
                return Ok(1.0 / value) if value else Error(InverseError.DIVISION_BY_ZERO)

            two = Ok(2.0)
            print(two.and_then(inverse).unwrap())  # 0.5

            zero = Ok(0.0)
            print(zero.and_then(inverse).unwrap_error())  # division by zero

            error = Error(1.0)
            print(error.and_then(inverse).unwrap_error())  # 1.0
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The bound result.
        """
        ...

    @required
    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        """Returns the result if it is an [`Error[E]`][wraps.result.Error],
        otherwise calls the asynchronous `function` with the wrapped value and returns the result.

        Example:
            ```python
            class InverseError(Enum):
                DIVISION_BY_ZERO = "division by zero"

            async def inverse(value: float) -> Result[float, InverseError]:
                return Ok(1.0 / value) if value else Error(InverseError.DIVISION_BY_ZERO)

            two = Ok(2.0)
            print((await two.and_then_await(inverse)).unwrap())  # 0.5

            zero = Ok(0.0)
            print((await zero.and_then_await(inverse)).unwrap_error())  # division by zero

            error = Error(1.0)
            print((await error.and_then_await(inverse)).unwrap_error())  # 1.0
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The bound result.
        """
        ...

    @required
    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        """Returns the result if it is [`Ok[T]`][wraps.result.Ok], otherwise calls the `function`
        with the wrapped error value and returns the result.

        Example:
            ```python
            class NonZeroError(Enum):
                ZERO = "the value is zero"

            def check_non_zero(value: int) -> Result[int, NonZeroError]:
                return Ok(value) if value else Error(NonZeroError.ZERO)

            five = Error(5)
            print(error.or_else(check_non_zero).unwrap())  # 13

            zero = Error(0)
            print(zero.or_else(check_non_zero).unwrap_error())  # the value is zero

            one = Ok(1)
            print(one.or_else(check_non_zero).unwrap())  # 1
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The bound result.
        """
        ...

    @required
    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        """Returns the result if it is [`Ok[T]`][wraps.result.Ok], otherwise calls the asynchronous
        `function` with the wrapped error value and returns the result.

        Example:
            ```python
            class NonZeroError(Enum):
                ZERO = "the value is zero"

            async def check_non_zero(value: int) -> Result[int, NonZeroError]:
                return Ok(value) if value else Error(NonZeroError.ZERO)

            five = Error(5)

            print((await error.or_else_await(check_non_zero)).unwrap())  # 13

            zero = Error(0)
            print((await zero.or_else_await(check_non_zero)).unwrap_error())  # the value is zero

            one = Ok(1)
            print((await ok.or_else_await(check_non_zero)).unwrap())  # 1
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The bound result.
        """
        ...

    def try_flatten(self: ResultProtocol[ResultProtocol[T, E], E]) -> Result[T, E]:
        """Flattens a [`Result[Result[T, E], E]`][wraps.result.Result]
        into a [`Result[T, E]`][wraps.result.Result].

        This is equivalent to [`result.and_then(identity)`][wraps.result.ResultProtocol.and_then].

        Example:
            ```python
            ok = Ok(42)
            ok_nested = Ok(ok)
            assert ok_nested.try_flatten() == ok

            error = Error(13)
            error_nested = Ok(error)
            assert error_nested.try_flatten() == error

            assert error.try_flatten() == error
            ```

        Returns:
            The flattened result.
        """
        return self.and_then(identity)  # type: ignore

    def try_flatten_error(self: ResultProtocol[T, ResultProtocol[T, E]]) -> Result[T, E]:
        """Flattens a [`Result[T, Result[T, E]]`][wraps.result.Result]
        into a [`Result[T, E]`][wraps.result.Result].

        This is equivalent to [`result.or_else(identity)`][wraps.result.ResultProtocol.or_else].

        Example:
            ```python
            ok = Ok(42)
            ok_nested = Error(ok)
            assert ok_nested.try_flatten_error() == error

            error = Error(13)
            error_nested = Error(error)
            assert error_nested.try_flatten_error() == error

            assert ok.try_flatten_error() == ok
            ```

        Returns:
            The flattened result.
        """
        return self.or_else(identity)  # type: ignore

    # def transpose(self: ResultProtocol[OptionProtocol[T], E]) -> Option[Result[T, E]]:
    #     """Transposes a result of an option into an option of a result.
    #     This function maps [`Result[Option[T], E]`][wraps.result.Result] into
    #     [`Option[Result[T, E]]`][wraps.option.Option] in the following way:

    #     - [`Ok(Null())`][wraps.result.Ok] is mapped to [`Null()`][wraps.option.Null];
    #     - [`Ok(Some(value))`][wraps.result.Ok] is mapped to
    #       [`Some(Ok(value))`][wraps.option.Some];
    #     - [`Error(error)`][wraps.result.Error] is mapped to
    #       [`Some(Error(error))`][wraps.option.Some].

    #     Example:
    #         ```python
    #         result = Ok(Some(64))
    #         option = Some(Ok(64)
    #         assert result.transpose() == option
    #         ```

    #     Returns:
    #         The transposed option.
    #     """
    #     return transpose_result(self)  # type: ignore

    @required
    def contains(self, value: U) -> bool:
        """Checks if the contained value is equal to the `value`.

        Example:
            ```python
            value = 42
            other = 69

            ok = Ok(value)
            assert ok.contains(value)
            assert not ok.contains(other)

            error = Error(value)
            assert not error.contains(value)
            ```

        Arguments:
            value: The value to check against.

        Returns:
            Whether the contained value is equal to the `value`.
        """
        ...

    @required
    def contains_error(self, error: F) -> bool:
        """Checks if the contained error value is equal to the `error`.

        Example:
            ```python
            value = 42
            other = 69

            error = Error(value)
            assert error.contains_error(value)
            assert not error.contains_error(other)

            ok = Ok(value)
            assert not ok.contains_error(value)
            ```

        Arguments:
            error: The error value to check against.

        Returns:
            Whether the contained error value is equal to the `error`.
        """
        ...

    @required
    def flip(self) -> Result[E, T]:
        """Converts a [`Result[T, E]`][wraps.result.Result]
        into a [`Result[E, T]`][wraps.result.Result].

        [`Ok(value)`][wraps.result.Ok] and [`Error(error)`][wraps.result.Error] get swapped to
        [`Error(value)`][wraps.result.Error] and [`Ok(error)`][wraps.result.Ok] respectively.

        Example:
            ```python
            value = 42

            result = Ok(value)
            flipped = Error(value)

            assert result.flip() == flipped
            ```

        Returns:
            The flipped result.
        """
        ...

    @required
    def into_ok_or_error(self: ResultProtocol[V, V]) -> V:
        """Returns the value contained within [`Result[V, V]`][wraps.result.Result], regardless
        of whether or not that result is [`Ok[V]`][wraps.result.Ok]
        or [`Error[V]`][wraps.result.Error].

        Example:
            ```python
            result: Result[int, int] = Ok(69)

            print(result.into_ok_or_error())  # 69; inferred `int`

            result = Error(42)

            print(result.into_ok_or_error())  # 42; inferred `int`
            ```

        Returns:
            The contained value, regardless of whether or not it is an error one.
        """
        ...

    @required
    def into_either(self) -> Either[T, E]:
        """Converts a [`Result[T, E]`][wraps.result.Result]
        into an [`Either[T, E]`][wraps.either.Either].

        [`Ok(value)`][wraps.result.Ok] is mapped to [`Left(value)`][wraps.either.Left]
        and [`Error(error)`][wraps.result.Error] is mapped to [`Right(error)`][wraps.either.Right].

        Example:
            ```python
            value = 42

            ok = Ok(value)
            left = Left(value)

            assert ok.into_either() == left

            error = Error(value)
            right = Right(value)

            assert error.into_either() == right
            ```

        Returns:
            The mapped either.
        """
        ...

    @required
    def early(self) -> T:
        """Functionally similar to the *question-mark* (`?`) operator in Rust.

        See [`early`][wraps.early] for more information.
        """
        ...


UNWRAP_ON_ERROR = "called `unwrap` on error"
UNWRAP_ERROR_ON_OK = "called `unwrap_error` on ok"


@final
@frozen()
class Ok(ResultProtocol[T, Never]):
    """[`Ok[T]`][wraps.result.Ok] variant of [`Result[T, E]`][wraps.result.Result]."""

    value: T

    @classmethod
    def create(cls, value: U) -> Ok[U]:
        return cls(value)  # type: ignore

    def is_ok(self) -> Literal[True]:
        return True

    def is_ok_and(self, predicate: Predicate[T]) -> bool:
        return predicate(self.value)

    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await predicate(self.value)

    def is_error(self) -> Literal[False]:
        return False

    def is_error_and(self, predicate: Predicate[E]) -> Literal[False]:
        return False

    async def is_error_and_await(self, predicate: AsyncPredicate[E]) -> Literal[False]:
        return False

    def expect(self, message: str) -> T:
        return self.value

    def expect_error(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: U) -> T:
        return self.value

    def unwrap_or_else(self, default: Nullary[U]) -> T:
        return self.value

    async def unwrap_or_else_await(self, default: AsyncNullary[U]) -> T:
        return self.value

    def unwrap_error(self) -> Never:
        panic(UNWRAP_ERROR_ON_OK)

    def unwrap_error_or(self, default: F) -> F:
        return default

    def unwrap_error_or_else(self, default: Nullary[F]) -> F:
        return default()

    async def unwrap_error_or_else_await(self, default: AsyncNullary[F]) -> F:
        return await default()

    def raising(self) -> T:
        return self.value

    def ok(self) -> Some[T]:
        return Some(self.value)

    def error(self) -> Null:
        return Null()

    def inspect(self, function: Inspect[T]) -> Ok[T]:
        function(self.value)

        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Ok[T]:
        await function(self.value)

        return self

    def inspect_error(self, function: Inspect[E]) -> Ok[T]:
        return self

    async def inspect_error_await(self, function: AsyncInspect[E]) -> Ok[T]:
        return self

    def map(self, function: Unary[T, U]) -> Ok[U]:
        return self.create(function(self.value))

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return function(self.value)

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    def map_error(self, function: Unary[E, F]) -> Ok[T]:
        return self

    def map_error_or(self, default: F, function: Unary[E, F]) -> F:
        return default

    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return default()

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    async def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        return await default()

    async def map_await(self, function: AsyncUnary[T, U]) -> Ok[U]:
        return self.create(await function(self.value))

    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await function(self.value)

    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await function(self.value)

    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await function(self.value)

    async def map_error_await(self, function: AsyncUnary[E, F]) -> Ok[T]:
        return self

    async def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return default

    async def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        return default()

    async def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await default()

    def iter(self) -> Iterator[T]:
        return once(self.value)

    def iter_error(self) -> Iterator[Never]:
        return empty()

    def async_iter(self) -> AsyncIterator[T]:
        return async_once(self.value)

    def async_iter_error(self) -> AsyncIterator[Never]:
        return async_empty()

    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return function(self.value)

    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        return await function(self.value)

    def or_else(self, function: Unary[E, Result[T, F]]) -> Ok[T]:
        return self

    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Ok[T]:
        return self

    def contains(self, value: U) -> bool:
        return self.value == value

    def contains_error(self, error: F) -> Literal[False]:
        return False

    def flip(self) -> Error[T]:
        return Error(self.value)

    def into_ok_or_error(self: Ok[V]) -> V:
        return self.value

    def into_either(self) -> Left[T]:
        return Left(self.value)

    def early(self) -> T:
        return self.value


@final
@frozen()
class Error(ResultProtocol[Never, E]):
    """[`Error[E]`][wraps.result.Error] variant of [`Result[T, E]`][wraps.result.Result]."""

    value: E

    def __bool__(self) -> Literal[False]:
        return False

    @classmethod
    def create(cls, error: F) -> Error[F]:
        return cls(error)  # type: ignore

    def is_ok(self) -> Literal[False]:
        return False

    def is_ok_and(self, predicate: Predicate[T]) -> Literal[False]:
        return False

    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> Literal[False]:
        return False

    def is_error(self) -> Literal[True]:
        return True

    def is_error_and(self, predicate: Predicate[E]) -> bool:
        return predicate(self.value)

    async def is_error_and_await(self, predicate: AsyncPredicate[E]) -> bool:
        return await predicate(self.value)

    def ok(self) -> Null:
        return Null()

    def error(self) -> Some[E]:
        return Some(self.value)

    def expect(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> Never:
        panic(UNWRAP_ON_ERROR)

    def expect_error(self, message: str) -> E:
        return self.value

    def unwrap_error(self) -> E:
        return self.value

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, default: Nullary[U]) -> U:
        return default()

    async def unwrap_or_else_await(self, default: AsyncNullary[U]) -> U:
        return await default()

    def unwrap_error_or(self, default: F) -> E:
        return self.value

    def unwrap_error_or_else(self, default: Nullary[F]) -> E:
        return self.value

    async def unwrap_error_or_else_await(self, default: AsyncNullary[F]) -> E:
        return self.value

    def raising(self: Error[AnyError]) -> Never:
        raise self.value

    def inspect(self, function: Inspect[T]) -> Error[E]:
        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Error[E]:
        return self

    def inspect_error(self, function: Inspect[E]) -> Error[E]:
        function(self.value)

        return self

    async def inspect_error_await(self, function: AsyncInspect[E]) -> Error[E]:
        await function(self.value)

        return self

    def map(self, function: Unary[T, U]) -> Error[E]:
        return self

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return default

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return default()

    def map_error(self, function: Unary[E, F]) -> Error[F]:
        return self.create(function(self.value))

    def map_error_or(self, default: F, function: Unary[E, F]) -> F:
        return function(self.value)

    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return function(self.value)

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await default()

    async def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        return function(self.value)

    async def map_await(self, function: AsyncUnary[T, U]) -> Error[E]:
        return self

    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return default

    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return default()

    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await default()

    async def map_error_await(self, function: AsyncUnary[E, F]) -> Error[F]:
        return self.create(await function(self.value))

    async def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return await function(self.value)

    async def map_error_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        return await function(self.value)

    async def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await function(self.value)

    def iter(self) -> Iterator[Never]:
        return empty()

    def iter_error(self) -> Iterator[E]:
        return once(self.value)

    def async_iter(self) -> AsyncIterator[Never]:
        return async_empty()

    def async_iter_error(self) -> AsyncIterator[E]:
        return async_once(self.value)

    def and_then(self, function: Unary[T, Result[U, E]]) -> Error[E]:
        return self

    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Error[E]:
        return self

    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return function(self.value)

    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await function(self.value)

    def contains(self, value: U) -> Literal[False]:
        return False

    def contains_error(self, error: F) -> bool:
        return self.value == error

    def flip(self) -> Ok[E]:
        return Ok(self.value)

    def into_ok_or_error(self: Error[V]) -> V:
        return self.value

    def into_either(self) -> Right[E]:
        return Right(self.value)

    def early(self) -> Never:
        raise EarlyResult(self.value)


Result = Union[Ok[T], Error[E]]
"""Result value, expressed as the union of [`Ok[T]`][wraps.result.Ok]
and [`Error[E]`][wraps.result.Error].
"""


def is_ok(result: Result[T, E]) -> TypeGuard[Ok[T]]:
    """This is the same as [`Result.is_ok`][wraps.result.ResultProtocol.is_ok],
    except it works as a *type guard*.
    """
    return result.is_ok()


def is_error(result: Result[T, E]) -> TypeGuard[Error[E]]:
    """This is the same as [`Result.is_error`][wraps.result.ResultProtocol.is_error],
    except it works as a *type guard*.
    """
    return result.is_error()


# import cycle solution
from wraps.either import Either, Left, Right
