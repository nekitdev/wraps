"""Error handling with the [`Result[T, E]`][wraps.result.Result] type.

[`Result[T, E]`][wraps.result.Result] is the type used for returning and propagating errors.

It is an enum with the variants, [`Ok[T]`][wraps.result.Ok],
representing success and containing a value,
and [`Err[E]`][wraps.result.Err], representing error and containing an error value.

Functions return [`Result[T, E]`][wraps.result.Result] whenever errors are expected and recoverable.

For instance, our `divide` function from the [`option`][wraps.option] section:

```python
# result.py

from enum import Enum

from wraps import Err, Ok, Result


class Error(Enum):
    DIVISION_BY_ZERO = "division by zero"


def divide(numerator: float, denominator: float) -> Result[float, Error]:
    return Ok(numerator / denominator) if denominator else Err(Error.DIVISION_BY_ZERO)
```

```python
from wraps import Err, Ok

from result import divide

result = divide(1.0, 2.0)

match result:
    case Ok(value):
        print(value)

    case Err(error):
        print(error.value)  # get the string `value` of the enumeration member
```
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    AsyncIterator,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Protocol,
    Type,
    TypeVar,
    Union,
    final,
)

from attrs import frozen
from funcs.decorators import wraps
from funcs.functions import identity
from typing_aliases import (
    AnyError,
    AsyncCallable,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    NormalError,
    Nullary,
    Predicate,
    Unary,
    required,
)
from typing_extensions import Callable, Never, ParamSpec, TypeIs

from wraps.errors import ErrorTypes
from wraps.iters import async_empty, async_once, empty, once
from wraps.panics import panic
from wraps.reprs import wrap_repr

__all__ = (
    # result
    "Result",
    "Ok",
    "Err",
    "is_ok",
    "is_err",
    # decorators
    "WrapResult",
    "WrapResultAwait",
    "wrap_result_on",
    "wrap_result_await_on",
    "wrap_result",
    "wrap_result_await",
)

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

            err = Err(13)
            assert not err.is_ok()
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

            err = Err(7)
            assert not err.is_ok_and(is_positive)
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

            err = Err(7)
            assert not await err.is_ok_and_await(is_positive)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

        Returns:
            Whether the result is [`Ok[T]`][wraps.result.Ok] and
            the asynchronous predicate is matched.
        """
        ...

    @required
    def is_err(self) -> bool:
        """Checks if the result is [`Err[E]`][wraps.result.Err].

        Example:
            ```python
            err = Err(34)
            assert err.is_err()

            ok = Ok(69)
            assert not ok.is_err()
            ```

        Returns:
            Whether the result is [`Err[E]`][wraps.result.Err].
        """
        ...

    @required
    def is_err_and(self, predicate: Predicate[E]) -> bool:
        """Checks if the result is [`Err[E]`][wraps.result.Err] and the value
        inside of it matches the `predicate`.

        Example:
            ```python
            def is_negative(value: int) -> bool:
                return value < 0

            err = Err(-13)
            assert err.is_err_and(is_positive)

            zero = Err(0)
            assert not zero.is_err_and(is_positive)

            ok = Ok(7)
            assert not ok.is_err_and(is_positive)
            ```

        Arguments:
            predicate: The predicate to check the contained value against.

        Returns:
            Whether the result is [`Err[E]`][wraps.result.Err] and the predicate is matched.
        """
        ...

    @required
    async def is_err_and_await(self, predicate: AsyncPredicate[E]) -> bool:
        """Checks if the result is [`Err[E]`][wraps.result.Err] and the value
        inside of it matches the asynchronous `predicate`.

        Example:
            ```python
            async def is_negative(value: int) -> bool:
                return value < 0

            err = Err(-13)
            assert await err.is_err_and_await(is_negative)

            zero = Err(0)
            assert not await zero.is_err_and_await(is_negative)

            ok = Ok(7)
            assert not await ok.is_err_and_await(is_negative)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

        Returns:
            Whether the result is [`Err[E]`][wraps.result.Err] and
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
            >>> err = Err(0)
            >>> err.expect("error!")
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: error!
            ```

        Arguments:
            message: The message used in panicking.

        Raises:
            Panic: Panics with the `message` if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    def expect_err(self, message: str) -> E:
        """Returns the contained [`Err[E]`][wraps.result.Err] value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> ok.expect_err("ok!")
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: ok!

            >>> err = Err(0)
            >>> err.expect_err("ok!")
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

        Instead, prefer to use pattern matching and handle the [`Err[E]`][wraps.result.Err]
        case explicitly, or call [`unwrap_or`][wraps.result.ResultProtocol.unwrap_or]
        or [`unwrap_or_else`][wraps.result.ResultProtocol.unwrap_or_else].

        Example:
            ```python
            >>> ok = Ok(13)
            >>> ok.unwrap()
            13

            >>> err = Err(0)
            >>> err.unwrap()
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: called `unwrap` on err
            ```

        Raises:
            Panic: Panics if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap_or(self, default: T) -> T:  # type: ignore[misc]
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value or the provided `default`.

        Example:
            ```python
            ok = Ok(69)
            assert ok.unwrap_or(0)

            err = Err(13)
            assert not err.unwrap_or(0)
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

            err = Err(8)
            assert not err.unwrap_or_else(int)
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

            err = Err(8)
            assert not await err.unwrap_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default-computing function to use.

        Returns:
            The contained value or the `await default()` one.
        """
        ...

    @required
    def or_raise(self, error: AnyError) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or raises the `error` provided.

        Arguments:
            error: The error to raise if the result is [`Err[E]`][wraps.result.Err].

        Raises:
            AnyError: The error provided, if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    def or_raise_with(self, error: Nullary[AnyError]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or raises the error computed from `error`.

        Arguments:
            error: The function computing the error to raise
                if the result is [`Err[E]`][wraps.result.Err].

        Raises:
            AnyError: The error computed, if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    async def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or raises the error computed asynchronously from `error`.

        Arguments:
            error: The asynchronous function computing the error to raise
                if the result is [`Err[E]`][wraps.result.Err].

        Raises:
            AnyError: The error computed, if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    def or_raise_from(self, error: Unary[E, AnyError]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or raises the error computed from `error` that receives the contained
        [`Err[E]`][wraps.result.Err] value.

        Arguments:
            error: The function computing the error to raise
                if the result is [`Err[E]`][wraps.result.Err].

        Raises:
            AnyError: The error computed, if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    async def or_raise_from_await(self, error: AsyncUnary[E, AnyError]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value
        or raise the error computed asynchronously from `error` that receives the contained
        [`Err[E]`][wraps.result.Err] value.

        Arguments:
            error: The asynchronous function computing the error to raise
                if the result is [`Err[E]`][wraps.result.Err].

        Raises:
            AnyError: The error computed, if the result is [`Err[E]`][wraps.result.Err].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap_err(self) -> E:
        """Returns the contained [`Err[E]`][wraps.result.Err] value.

        Because this function may panic, its use is generally discouraged.

        Instead, prefer to use pattern matching and handle the [`Ok[T]`][wraps.result.Ok]
        case explicitly, or call [`unwrap_err_or`][wraps.result.ResultProtocol.unwrap_err_or]
        or [`unwrap_err_or_else`][wraps.result.ResultProtocol.unwrap_err_or_else].

        Example:
            ```python
            >>> err = Err(13)
            >>> err.unwrap_err()
            13

            >>> ok = Ok(42)
            >>> ok.unwrap_err()
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: called `unwrap_err` on ok
            ```

        Raises:
            Panic: Panics if the result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained error value.
        """
        ...

    @required
    def unwrap_err_or(self, default: E) -> E:  # type: ignore[misc]
        """Returns the contained [`Err[E]`][wraps.result.Err] value (of type `E`)
        or a provided default.

        Example:
            ```python
            err = Err(1)
            assert err.unwrap_err_or(0)

            ok = Ok(2)
            assert not ok.unwrap_err_or(0)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained error value or the `default` one.
        """
        ...

    @required
    def unwrap_err_or_else(self, default: Nullary[E]) -> E:
        """Returns the contained [`Err[E]`][wraps.result.Err] value
        or computes it from the `default` function.

        Example:
            ```python
            err = Err(5)
            assert err.unwrap_err_or_else(int)

            ok = Ok(8)
            assert not ok.unwrap_err_or_else(int)

        Arguments:
            default: The default-computing function to use.

        Returns:
            The contained error value or the `default()` one.
        """
        ...

    @required
    async def unwrap_err_or_else_await(self, default: AsyncNullary[E]) -> E:
        """Returns the contained [`Err[E]`][wraps.result.Err] value
        or computes it from the asynchronous `default` function.

        Example:
            ```python
            async def default() -> int:
                return 0

            err = Err(13)
            assert await err.unwrap_err_or_else_await(default)

            ok = Ok(5)
            assert not await ok.unwrap_err_or_else_await(default)
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
        contained [`Err[AnyError]`][wraps.result.Err] value.

        Example:
            ```python
            >>> ok = Ok(13)
            >>> ok.raising()
            13

            >>> err = Err(ValueError("error..."))
            >>> err.raising()
            Traceback (most recent call last):
              ...
            ValueError: error...
            ```

        Raises:
            AnyError: The contained error, if the result is [`Err[AnyError]`][wraps.result.Err].

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

            err = Err(0)

            assert err.ok().is_null()
            ```

        Returns:
            The converted option.
        """
        ...

    @required
    def err(self) -> Option[E]:
        """Converts a [`Result[T, E]`][wraps.result.Result]
        into an [`Option[E]`][wraps.option.Option].

        Converts `self` into an [`Option[E]`][wraps.option.Option],
        discarding success values, if any.

        Example:
            ```python
            err = Err(13)

            assert err.err().is_some()

            ok = Ok(2)

            assert ok.err().is_null()
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
    def inspect_err(self, function: Inspect[E]) -> Result[T, E]:
        """Inspects a possibly contained [`Err[E]`][wraps.result.Err] value.

        Example:
            ```python
            err = Err("Bye, world!")

            same = err.inspect_err(print)  # Bye, world!

            assert err == same
            ```

        Arguments:
            function: The error-inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @required
    async def inspect_err_await(self, function: AsyncInspect[E]) -> Result[T, E]:
        """Inspects a possibly contained [`Err[E]`][wraps.result.Err] value.

        Example:
            ```python
            async def function(value: str) -> None:
                print(value)

            err = Err("Bye, world!")

            same = await err.inspect_err_await(function)  # Bye, world!

            assert err == same
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
        leaving any [`Err[E]`][wraps.result.Err] values untouched.

        This function can be used to compose the results of two functions.

        Example:
            ```python
            value = 69
            mapped = "69"

            ok = Ok(value)

            assert ok.map(str) == Ok(mapped)

            err = Err(0)

            assert err.map(str) == err
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

            err = Err("error...")
            print(err.map_or(42, len))  # 42
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

            err = Err("error!")
            print(err.map_or_else(int, len))  # 0
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

            err = Err("error!")
            print(await err.map_or_else_await(default, len))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    def map_err(self, function: Unary[E, F]) -> Result[T, F]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[T, F]`][wraps.result.Result]
        by applying the `function` to the contained [`Err[E]`][wraps.result.Err] value,
        leaving any [`Ok[T]`][wraps.result.Ok] values untouched.

        Example:
            ```python
            value = 42
            mapped = "42"

            err = Err(value)

            assert err.map_err(str) == Err(mapped)

            ok = Ok(2)

            assert ok.map_err(str) == ok
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    def map_err_or(self, default: F, function: Unary[E, F]) -> F:
        """Returns the default value (if succeeded), or applies the `function`
        to the contained error value (if errored).

        Example:
            ```python
            err = Err("nekit")
            print(err.map_err_or(13, len))  # 5

            ok = Ok("ok")
            print(ok.map_err_or(13, len))  # 13
            ```

        Arguments:
            default: The default value to use.
            function: The function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    def map_err_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the `function`
        to the contained value (if errored).

        Example:
            ```python
            err = Err("error...")
            print(err.map_err_or_else(int, len))  # 8

            ok = Ok("ok!")
            print(ok.map_err_or_else(int, len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_err_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the `function`
        to the contained value (if errored).

        Example:
            ```python
            err = Err("error...")
            print(await err.map_err_or_else(int, len))  # 8

            ok = Ok("ok!")
            print(await ok.map_err_or_else(int, len))  # 0
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
        leaving any [`Err[E]`][wraps.result.Err] values untouched.

        This function can be used to compose the results of two functions.

        Example:
            ```python
            async def function(value: int) -> str:
                return str(value)

            value = 69
            mapped = "69"

            ok = Ok(value)

            assert await ok.map_await(function) == Ok(mapped)

            err = Err(0)

            assert await err.map_await(function) == err
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

            err = Err("error...")
            print(err.map_await_or(42, function))  # 42
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

            err = Err("error!")
            print(await err.map_await_or_else(int, async_len))  # 0
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

            err = Err("error!")
            print(await err.map_await_or_else_await(default, function))  # 0
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_err_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        """Maps a [`Result[T, E]`][wraps.result.Result] to a [`Result[T, F]`][wraps.result.Result]
        by applying the asynchronous `function` to the contained [`Err[E]`][wraps.result.Err]
        value, leaving any [`Ok[T]`][wraps.result.Ok] values untouched.

        Example:
            ```python
            async def function(value: int) -> str:
                return str(value)

            value = 42
            mapped = "42"

            err = Err(value)

            assert await err.map_err_await(function) == Err(mapped)

            ok = Ok(13)

            assert await ok.map_err_await(function) == ok
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped result.
        """
        ...

    @required
    async def map_err_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        """Returns the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            err = Err("Bye, world!")
            print(await err.map_err_await_or(42, function))  # 11

            ok = Ok("Hello, world!")
            print(await ok.map_err_await_or(42, function))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @required
    async def map_err_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            err = Err("Bye, world!")
            print(await err.map_err_await_or_else(int, async_len))  # 11

            ok = Ok("Hello, world!")
            print(await ok.map_err_await_or_else(int, async_len))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the computed default value.
        """
        ...

    @required
    async def map_err_await_or_else_await(
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

            err = Err("error")
            print(await err.map_err_await_or_else_await(default, function))  # 5

            ok = Ok("ok")
            print(await ok.map_err_await_or_else_await(default, function))  # 0
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
            >>> err = Err(13)
            >>> next(err.iter(), 0)
            0
            ```

        Returns:
            An iterator over the possibly contained value.
        """
        ...

    @required
    def iter_err(self) -> Iterator[E]:
        """Returns an iterator over the possibly contained error value.

        Example:
            ```python
            >>> err = Err(13)
            >>> next(err.iter_err(), 0)
            13
            >>> ok = Ok(1)
            >>> next(ok.iter_err(), 0)
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
            >>> err = Err(13)
            >>> await async_next(err.async_iter(), 0)
            0
            ```

        Returns:
            An asynchronous iterator over the possibly contained value.
        """
        ...

    @required
    def async_iter_err(self) -> AsyncIterator[E]:
        """Returns an asynchronous iterator over the possibly contained
        [`Err[E]`][wraps.result.Err] value.

        Example:
            ```python
            >>> err = Err(42)
            >>> await async_next(err.async_iter_err(), 0)
            42
            >>> ok = Ok(13)
            >>> await async_next(ok.async_iter_err(), 0)
            0
            ```

        Returns:
            An asynchronous iterator over the possibly contained error value.
        """
        ...

    @required
    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        """Returns the result if it is an [`Err[E]`][wraps.result.Err],
        otherwise calls the `function` with the wrapped value and returns the result.

        This function is also known as *bind* in functional programming.

        Example:
            ```python
            def inverse(value: float) -> Result[float, str]:
                return Ok(1.0 / value) if value else Err("division by zero")

            two = Ok(2.0)
            print(two.and_then(inverse).unwrap())  # 0.5

            zero = Ok(0.0)
            print(zero.and_then(inverse).unwrap_err())  # division by zero

            err = Err(1.0)
            print(err.and_then(inverse).unwrap_err())  # 1.0
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The bound result.
        """
        ...

    @required
    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        """Returns the result if it is an [`Err[E]`][wraps.result.Err],
        otherwise calls the asynchronous `function` with the wrapped value and returns the result.

        Example:
            ```python
            async def inverse(value: float) -> Result[float, str]:
                return Ok(1.0 / value) if value else Err("division by zero")

            two = Ok(2.0)
            print((await two.and_then_await(inverse)).unwrap())  # 0.5

            zero = Ok(0.0)
            print((await zero.and_then_await(inverse)).unwrap_err())  # division by zero

            err = Err(1.0)
            print((await err.and_then_await(inverse)).unwrap_err())  # 1.0
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
            def check_non_zero(value: int) -> Result[int, str]:
                return Ok(value) if value else Err("the value is zero")

            err = Err(5)
            print(err.or_else(check_non_zero).unwrap())  # 5

            zero = Err(0)
            print(zero.or_else(check_non_zero).unwrap_err())  # the value is zero

            ok = Ok(1)
            print(ok.or_else(check_non_zero).unwrap())  # 1
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
            async def check_non_zero(value: int) -> Result[int, str]:
                return Ok(value) if value else Err("the value is zero")

            err = Err(5)

            print((await err.or_else_await(check_non_zero)).unwrap())  # 5

            zero = Err(0)
            print((await zero.or_else_await(check_non_zero)).unwrap_err())  # the value is zero

            ok = Ok(1)
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

            err = Err(13)
            err_nested = Ok(err)
            assert err_nested.try_flatten() == err

            assert err.try_flatten() == err
            ```

        Returns:
            The flattened result.
        """
        return self.and_then(identity)  # type: ignore[arg-type]

    def try_flatten_err(self: ResultProtocol[T, ResultProtocol[T, E]]) -> Result[T, E]:
        """Flattens a [`Result[T, Result[T, E]]`][wraps.result.Result]
        into a [`Result[T, E]`][wraps.result.Result].

        This is equivalent to [`result.or_else(identity)`][wraps.result.ResultProtocol.or_else].

        Example:
            ```python
            ok = Ok(42)
            ok_nested = Err(ok)
            assert ok_nested.try_flatten_err() == err

            err = Err(13)
            err_nested = Err(err)
            assert err_nested.try_flatten_err() == err

            assert ok.try_flatten_err() == ok
            ```

        Returns:
            The flattened result.
        """
        return self.or_else(identity)  # type: ignore[arg-type]

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

            err = Err(value)
            assert not err.contains(value)
            ```

        Arguments:
            value: The value to check against.

        Returns:
            Whether the contained value is equal to the `value`.
        """
        ...

    @required
    def contains_err(self, error: F) -> bool:
        """Checks if the contained error value is equal to the `error`.

        Example:
            ```python
            value = 42
            other = 69

            err = Err(value)
            assert err.contains_err(value)
            assert not err.contains_err(other)

            ok = Ok(value)
            assert not ok.contains_err(value)
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

        [`Ok(value)`][wraps.result.Ok] and [`Err(error)`][wraps.result.Err] get swapped to
        [`Err(value)`][wraps.result.Err] and [`Ok(error)`][wraps.result.Ok] respectively.

        Example:
            ```python
            value = 42

            result = Ok(value)
            flipped = Err(value)

            assert result.flip() == flipped
            ```

        Returns:
            The flipped result.
        """
        ...

    @required
    def into_ok_or_err(self: ResultProtocol[V, V]) -> V:
        """Returns the value contained within [`Result[V, V]`][wraps.result.Result], regardless
        of whether or not that result is [`Ok[V]`][wraps.result.Ok]
        or [`Err[V]`][wraps.result.Err].

        Example:
            ```python
            result: Result[int, int] = Ok(69)

            print(result.into_ok_or_err())  # 69; inferred `int`

            result = Err(42)

            print(result.into_ok_or_err())  # 42; inferred `int`
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
        and [`Err(error)`][wraps.result.Err] is mapped to [`Right(error)`][wraps.either.Right].

        Example:
            ```python
            value = 42

            ok = Ok(value)
            left = Left(value)

            assert ok.into_either() == left

            err = Err(value)
            right = Right(value)

            assert err.into_either() == right
            ```

        Returns:
            The mapped either.
        """
        ...

    @required
    def early(self) -> T:
        """Functionally similar to the *question-mark* (`?`) operator in Rust.

        Calls to this method are to be combined with
        [`@early_result`][wraps.early.decorators.early_result] decorators to work properly.
        """
        ...


UNWRAP_ON_ERR = "called `unwrap` on err"
UNWRAP_ERR_ON_OK = "called `unwrap_err` on ok"


@final
@frozen()
class Ok(ResultProtocol[T, Never]):
    """[`Ok[T]`][wraps.result.Ok] variant of [`Result[T, E]`][wraps.result.Result]."""

    value: T

    def __repr__(self) -> str:
        return wrap_repr(self, self.value)

    @classmethod
    def create(cls, value: U) -> Ok[U]:
        return cls(value)  # type: ignore[arg-type, return-value]

    def is_ok(self) -> Literal[True]:
        return True

    def is_ok_and(self, predicate: Predicate[T]) -> bool:
        return predicate(self.value)

    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await predicate(self.value)

    def is_err(self) -> Literal[False]:
        return False

    def is_err_and(self, predicate: Predicate[E]) -> Literal[False]:
        return False

    async def is_err_and_await(self, predicate: AsyncPredicate[E]) -> Literal[False]:
        return False

    def expect(self, message: str) -> T:
        return self.value

    def expect_err(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: U) -> T:
        return self.value

    def unwrap_or_else(self, default: Nullary[U]) -> T:
        return self.value

    async def unwrap_or_else_await(self, default: AsyncNullary[U]) -> T:
        return self.value

    def or_raise(self, error: AnyError) -> T:
        return self.value

    def or_raise_with(self, error: Nullary[AnyError]) -> T:
        return self.value

    async def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> T:
        return self.value

    def or_raise_from(self, error: Unary[E, AnyError]) -> T:
        return self.value

    async def or_raise_from_await(self, error: AsyncUnary[E, AnyError]) -> T:
        return self.value

    def unwrap_err(self) -> Never:
        panic(UNWRAP_ERR_ON_OK)

    def unwrap_err_or(self, default: F) -> F:
        return default

    def unwrap_err_or_else(self, default: Nullary[F]) -> F:
        return default()

    async def unwrap_err_or_else_await(self, default: AsyncNullary[F]) -> F:
        return await default()

    def raising(self) -> T:
        return self.value

    def ok(self) -> Some[T]:
        return Some(self.value)

    def err(self) -> Null:
        return NULL

    def inspect(self, function: Inspect[T]) -> Ok[T]:
        function(self.value)

        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Ok[T]:
        await function(self.value)

        return self

    def inspect_err(self, function: Inspect[E]) -> Ok[T]:
        return self

    async def inspect_err_await(self, function: AsyncInspect[E]) -> Ok[T]:
        return self

    def map(self, function: Unary[T, U]) -> Ok[U]:
        return self.create(function(self.value))

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return function(self.value)

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    def map_err(self, function: Unary[E, F]) -> Ok[T]:
        return self

    def map_err_or(self, default: F, function: Unary[E, F]) -> F:
        return default

    def map_err_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return default()

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    async def map_err_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
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

    async def map_err_await(self, function: AsyncUnary[E, F]) -> Ok[T]:
        return self

    async def map_err_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return default

    async def map_err_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        return default()

    async def map_err_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await default()

    def iter(self) -> Iterator[T]:
        return once(self.value)

    def iter_err(self) -> Iterator[Never]:
        return empty()

    def async_iter(self) -> AsyncIterator[T]:
        return async_once(self.value)

    def async_iter_err(self) -> AsyncIterator[Never]:
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

    def contains_err(self, error: F) -> Literal[False]:
        return False

    def flip(self) -> Err[T]:
        return Err(self.value)

    def into_ok_or_err(self: Ok[V]) -> V:
        return self.value

    def into_either(self) -> Left[T]:
        return Left(self.value)

    def early(self) -> T:
        return self.value


@final
@frozen()
class Err(ResultProtocol[Never, E]):
    """[`Err[E]`][wraps.result.Err] variant of [`Result[T, E]`][wraps.result.Result]."""

    value: E

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return wrap_repr(self, self.value)

    @classmethod
    def create(cls, error: F) -> Err[F]:
        return cls(error)  # type: ignore[arg-type, return-value]

    def is_ok(self) -> Literal[False]:
        return False

    def is_ok_and(self, predicate: Predicate[T]) -> Literal[False]:
        return False

    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> Literal[False]:
        return False

    def is_err(self) -> Literal[True]:
        return True

    def is_err_and(self, predicate: Predicate[E]) -> bool:
        return predicate(self.value)

    async def is_err_and_await(self, predicate: AsyncPredicate[E]) -> bool:
        return await predicate(self.value)

    def ok(self) -> Null:
        return NULL

    def err(self) -> Some[E]:
        return Some(self.value)

    def expect(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> Never:
        panic(UNWRAP_ON_ERR)

    def expect_err(self, message: str) -> E:
        return self.value

    def unwrap_err(self) -> E:
        return self.value

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, default: Nullary[U]) -> U:
        return default()

    async def unwrap_or_else_await(self, default: AsyncNullary[U]) -> U:
        return await default()

    def or_raise(self, error: AnyError) -> Never:
        raise error

    def or_raise_with(self, error: Nullary[AnyError]) -> Never:
        raise error()

    async def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> Never:
        raise await error()

    def or_raise_from(self, error: Unary[E, AnyError]) -> Never:
        raise error(self.value)

    async def or_raise_from_await(self, error: AsyncUnary[E, AnyError]) -> Never:
        raise await error(self.value)

    def unwrap_err_or(self, default: F) -> E:
        return self.value

    def unwrap_err_or_else(self, default: Nullary[F]) -> E:
        return self.value

    async def unwrap_err_or_else_await(self, default: AsyncNullary[F]) -> E:
        return self.value

    def raising(self: Err[AnyError]) -> Never:
        raise self.value

    def inspect(self, function: Inspect[T]) -> Err[E]:
        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Err[E]:
        return self

    def inspect_err(self, function: Inspect[E]) -> Err[E]:
        function(self.value)

        return self

    async def inspect_err_await(self, function: AsyncInspect[E]) -> Err[E]:
        await function(self.value)

        return self

    def map(self, function: Unary[T, U]) -> Err[E]:
        return self

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return default

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return default()

    def map_err(self, function: Unary[E, F]) -> Err[F]:
        return self.create(function(self.value))

    def map_err_or(self, default: F, function: Unary[E, F]) -> F:
        return function(self.value)

    def map_err_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        return function(self.value)

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await default()

    async def map_err_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        return function(self.value)

    async def map_await(self, function: AsyncUnary[T, U]) -> Err[E]:
        return self

    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return default

    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return default()

    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await default()

    async def map_err_await(self, function: AsyncUnary[E, F]) -> Err[F]:
        return self.create(await function(self.value))

    async def map_err_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        return await function(self.value)

    async def map_err_await_or_else(self, default: Nullary[F], function: AsyncUnary[E, F]) -> F:
        return await function(self.value)

    async def map_err_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        return await function(self.value)

    def iter(self) -> Iterator[Never]:
        return empty()

    def iter_err(self) -> Iterator[E]:
        return once(self.value)

    def async_iter(self) -> AsyncIterator[Never]:
        return async_empty()

    def async_iter_err(self) -> AsyncIterator[E]:
        return async_once(self.value)

    def and_then(self, function: Unary[T, Result[U, E]]) -> Err[E]:
        return self

    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Err[E]:
        return self

    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return function(self.value)

    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await function(self.value)

    def contains(self, value: U) -> Literal[False]:
        return False

    def contains_err(self, error: F) -> bool:
        return self.value == error

    def flip(self) -> Ok[E]:
        return Ok(self.value)

    def into_ok_or_err(self: Err[V]) -> V:
        return self.value

    def into_either(self) -> Right[E]:
        return Right(self.value)

    def early(self) -> Never:
        raise EarlyResult(self.value)


Result = Union[Ok[T], Err[E]]
"""Result value, expressed as the union of [`Ok[T]`][wraps.result.Ok]
and [`Err[E]`][wraps.result.Err].
"""


def is_ok(result: Result[T, E]) -> TypeIs[Ok[T]]:
    """This is the same as [`Result.is_ok`][wraps.result.ResultProtocol.is_ok],
    except it works as a *type guard*.
    """
    return result.is_ok()


def is_err(result: Result[T, E]) -> TypeIs[Err[E]]:
    """This is the same as [`Result.is_err`][wraps.result.ResultProtocol.is_err],
    except it works as a *type guard*.
    """
    return result.is_err()


# import cycle solution

from wraps.early.errors import EarlyResult
from wraps.either import Either, Left, Right
from wraps.option import NULL, Null, Option, Some

if TYPE_CHECKING:
    from wraps.typing import ResultAsyncCallable, ResultCallable

P = ParamSpec("P")

A = TypeVar("A", bound=AnyError)


@final
@frozen()
class WrapResult(Generic[A]):
    """Wraps functions returning `T` into functions returning
    [`Result[T, E]`][wraps.result.Result].

    Errors are handled via returning [`Err(error)`][wraps.result.Err] on `error` of
    [`error_types`][wraps.result.WrapResult.error_types], wrapping the resulting
    `value` into [`Ok(value)`][wraps.result.Ok].
    """

    error_types: ErrorTypes[A]
    """The error types to handle. See [`ErrorTypes[A]`][wraps.errors.ErrorTypes]."""

    def __call__(self, function: Callable[P, T]) -> ResultCallable[P, T, A]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, A]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_types.extract() as error:
                return Err(error)

        return wrap


def wrap_result_on(head: Type[A], *tail: Type[A]) -> WrapResult[A]:
    """Creates [`WrapResult[A]`][wraps.result.WrapResult] decorators.

    This function enforces at least one error type to be provided.

    Example:
        ```python
        @wrap_result_on(ValueError)
        def parse(string: str) -> int:
            return int(string)

        assert parse("128").is_ok()
        assert parse("owo").is_err()
        ```

    Arguments:
        head: The head of the error types to handle.
        *tail: The tail of the error types to handle.

    Returns:
        The [`WrapResult[A]`][wraps.result.WrapResult] decorator created.
    """
    return WrapResult(ErrorTypes[A].from_head_and_tail(head, *tail))


wrap_result = wrap_result_on(NormalError)
"""An instance of [`WrapResult[NormalError]`][wraps.result.WrapResult]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapResultAwait(Generic[A]):
    """Wraps asynchronous functions returning `T` into asynchronous functions returning
    [`Result[T, E]`][wraps.result.Result].

    Errors are handled via returning [`Err(error)`][wraps.result.Err] on `error` of
    [`error_types`][wraps.result.WrapResult.error_types], wrapping the resulting
    `value` into [`Ok(value)`][wraps.result.Ok].
    """

    error_types: ErrorTypes[A]
    """The error types to handle. See [`ErrorTypes[A]`][wraps.errors.ErrorTypes]."""

    def __call__(self, function: AsyncCallable[P, T]) -> ResultAsyncCallable[P, T, A]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, A]:
            try:
                return Ok(await function(*args, **kwargs))

            except self.error_types.extract() as error:
                return Err(error)

        return wrap


def wrap_result_await_on(head: Type[A], *tail: Type[A]) -> WrapResultAwait[A]:
    """Creates [`WrapResultAwait[A]`][wraps.result.WrapResultAwait] decorators.

    This function enforces at least one error type to be provided.

    Example:
        ```python
        @wrap_result_await_on(ValueError)
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("128")).is_ok()
        assert (await parse("owo")).is_err()
        ```

    Arguments:
        head: The head of the error types to handle.
        *tail: The tail of the error types to handle.

    Returns:
        The [`WrapResultAwait[A]`][wraps.result.WrapResultAwait] decorator created.
    """
    return WrapResultAwait(ErrorTypes[A].from_head_and_tail(head, *tail))


wrap_result_await = wrap_result_await_on(NormalError)
"""An instance of [`WrapResultAwait[NormalError]`][wraps.result.WrapResultAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""
