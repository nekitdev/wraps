from __future__ import annotations

from abc import abstractmethod
from functools import wraps
from typing import (
    TYPE_CHECKING,
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterator,
    Optional,
    Type,
    TypeVar,
    Union,
    final,
    overload,
)

from attrs import frozen
from typing_extensions import Literal, Never, ParamSpec, Protocol, TypeGuard

from wraps.errors import ResultShortcut, panic
from wraps.option import Null, Option, OptionProtocol, Some, is_some
from wraps.typing import (
    AnyException,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)

__all__ = ("Result", "Ok", "Error", "is_ok", "is_error", "wrap_result")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")

E = TypeVar("E", covariant=True)
F = TypeVar("F")

V = TypeVar("V")


def identity(value: V) -> V:
    return value


UNWRAP_ON_ERROR = "called `unwrap` on error"
UNWRAP_ERROR_ON_OK = "called `unwrap_error` on ok"


class ResultProtocol(Protocol[T, E]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter()

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    async def is_ok_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        """Checks if the result is [`Ok[T]`][wraps.result.Ok] and the value
        inside of it matches the asynchronous `predicate`.

        Example:
            ```python
            def is_positive(value: int) -> bool:
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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
            Panic: Panics with `message` if the result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
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

    @abstractmethod
    def unwrap_or(self, default: T) -> T:  # type: ignore
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`)
        or a provided default.

        Example:
            ```python
            default = 0

            ok = Ok(69)
            assert ok.unwrap_or(default)

            error = Error(0)
            assert not error.unwrap_or(default)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained value or `default` one.
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, default: Nullary[T]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`) or
        computes it from the function.

        Example:
            ```python
            ok = Ok(5)
            assert ok.unwrap_or_else(int)

            error = Error(8)
            assert not error.unwrap_or_else(int)

        Arguments:
            default: The default function to use.

        Returns:
            The contained value or `default()` one.
        """
        ...

    @abstractmethod
    async def unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`) or
        computes it from the asynchronous function.

        Example:
            ```python
            async def default() -> int:
                return 0

            ok = Ok(5)
            assert await ok.unwrap_or_else_await(default)

            error = Error(8)
            assert not await error.unwrap_or_else_await(default)

        Arguments:
            default: The asynchronous default function to use.

        Returns:
            The contained value or `await default()` one.
        """
        ...

    @abstractmethod
    def unwrap_or_raise(self, exception: AnyException) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`) or
        raises an exception.

        Example:
            ```python
            >>> exception = ValueError("error!")

            >>> ok = Ok(42)
            >>> ok.unwrap_or_raise(exception)
            42

            >>> error = Error(1)
            >>> error.unwrap_or_raise(exception)
            Traceback (most recent call last):
              ...
            ValueError: error!
            ```

        Arguments:
            exception: The exception to raise.

        Raises:
            AnyException: The exception given, if result is [`Error[E]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    def unwrap_or_raise_with(self, function: Nullary[AnyException]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`) or
        raises an exception computed from `function`.

        Example:
            >>> def function() -> ValueError:
            ...     return ValueError("error!")

            >>> ok = Ok(13)
            >>> ok.unwrap_or_raise_with(function)
            13

            >>> error = Error(0)
            >>> error.unwrap_or_raise_with(function)
            Traceback (most recent call last):
              ...
            ValueError: error!
            ```

        Arguments:
            function: The exception-generating function to use.

        Raises:
            AnyException: The computed exception, if result is [`Error[E]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    async def unwrap_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> T:
        """Returns the contained [`Ok[T]`][wraps.result.Ok] value (of type `T`) or
        raises an exception computed from asynchronous `function`.

        Example:
            >>> async def function() -> ValueError:
            ...     return ValueError("error...")

            >>> ok = Ok(42)
            >>> await ok.unwrap_or_raise_with_await(function)
            42

            >>> error = Error(5)
            >>> await error.unwrap_or_raise_with_await(function)
            Traceback (most recent call last):
              ...
            ValueError: error...
            ```

        Arguments:
            function: The asynchronous exception-generating function to use.

        Raises:
            AnyException: The computed exception, if result is [`Error[E]`][wraps.result.Error].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    def unwrap_error(self) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`).

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

    @abstractmethod
    def unwrap_error_or(self, default: E) -> E:  # type: ignore
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`)
        or a provided default.

        Example:
            ```python
            default = 0

            error = Error(1)
            assert error.unwrap_error_or(default)

            ok = Ok(2)
            assert not ok.unwrap_error_or(default)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained error value or `default` one.
        """
        ...

    @abstractmethod
    def unwrap_error_or_else(self, default: Nullary[E]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`) or
        computes it from the function.

        Example:
            ```python
            error = Error(5)
            assert error.unwrap_error_or_else(int)

            ok = Ok(8)
            assert not ok.unwrap_error_or_else(int)

        Arguments:
            default: The default function to use.

        Returns:
            The contained error value or `default()` one.
        """
        ...

    @abstractmethod
    async def unwrap_error_or_else_await(self, default: AsyncNullary[E]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`) or
        computes it from the asynchronous function.

        Example:
            ```python
            async def default() -> int:
                return 0

            error = Error(13)
            assert await error.unwrap_error_or_else_await(default)

            ok = Ok(5)
            assert not ok.unwrap_error_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default function to use.

        Returns:
            The contained error value or `await default()` one."""

    @abstractmethod
    def unwrap_error_or_raise(self, exception: AnyException) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`) or
        raises an exception.

        Example:
            ```python
            >>> exception = ValueError("ok!")

            >>> error = Error(0)
            >>> error.unwrap_error_or_raise(exception)
            0

            >>> ok = Ok(42)
            >>> ok.unwrap_error_or_raise(exception)
            Traceback (most recent call last):
              ...
            ValueError: ok!
            ```

        Arguments:
            exception: The exception to raise.

        Returns:
            The contained value.
        """
        ...

    def unwrap_error_or_raise_with(self, function: Nullary[AnyException]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`) or
        raises an exception computed from `function`.

        Example:
            >>> def function() -> ValueError:
            ...     return ValueError("error!")

            >>> error = Error(0)
            >>> error.unwrap_error_or_raise_with(function)
            0

            >>> ok = Ok(42)
            >>> ok.unwrap_error_or_raise_with(function)
            Traceback (most recent call last):
              ...
            ValueError: error!
            ```

        Arguments:
            function: The exception-generating function to use.

        Raises:
            AnyException: The computed exception, if result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    async def unwrap_error_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> E:
        """Returns the contained [`Error[E]`][wraps.result.Error] value (of type `E`) or
        raises an exception computed from asynchronous `function`.

        Example:
            >>> async def function() -> ValueError:
            ...     return ValueError("ok...")

            >>> error = Error(5)
            >>> await error.unwrap_error_or_raise_with_await(function)
            5

            >>> ok = Ok(13)
            >>> await ok.unwrap_error_or_raise_with_await(function)
            Traceback (most recent call last):
              ...
            ValueError: ok...
            ```

        Arguments:
            function: The asynchronous exception-generating function to use.

        Raises:
            AnyException: The computed exception, if result is [`Ok[T]`][wraps.result.Ok].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    def ok(self) -> Option[T]:
        """Converts [`Result[T, E]`][wraps.result.Result] to [`Option[T]`][wraps.option.Option].

        Converts `self` into an [`Option[T]`][wraps.option.Option], discarding the error, if any.

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

    @abstractmethod
    def error(self) -> Option[E]:
        """Converts [`Result[T, E]`][wraps.result.Result] to [`Option[E]`][wraps.option.Option].

        Converts `self` into an [`Option[E]`][wraps.option.Option], discarding the success value,
        if any.

        Example:
            ```python
            error = Error(13)

            assert error.error().is_some()

            ok = Ok(2)

            assert error.ok().is_null()
            ```

        Returns:
            The converted option.
        """
        ...

    @abstractmethod
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

    @abstractmethod
    def inspect_error(self, function: Inspect[E]) -> Result[T, E]:
        """Inspects a possibly contained [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            error = Error("Bye, world!")

            same = error.inspect_error(print)  # Bye, world!

            assert error == same
            ```

        Arguments:
            function: The inspecting function.

        Returns:
            The inspected result.
        """
        ...

    @abstractmethod
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
            function: The inspecting asynchronous function.

        Returns:
            The inspected result.
        """
        ...

    @abstractmethod
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
            function: The inspecting asynchronous function.

        Returns:
            The inspected result.
        """
        ...

    @abstractmethod
    def map(self, function: Unary[T, U]) -> Result[U, E]:
        """Maps [`Result[T, E]`][wraps.result.Result] to [`Result[U, E]`][wraps.result.Result]
        by applying `function` to the contained [`Ok[T]`][wraps.result.Ok] value,
        leaving any [`Error[E]`][wraps.result.Error] untouched.

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

    @abstractmethod
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        """Returns the default value (if errored), or applies `function`
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

    @abstractmethod
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if errored), or applies `function`
        to the contained value (if succeeded).

        Example:
            ```python
            ok = Ok("Hello, world!")
            print(ok.map_or_else(int, len))  # 13

            error = Error("error!")
            print(error.map_or_else(int, len))  # 0
            ```

        Arguments:
            default: The default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if errored), or applies the `function`
        to the contained value (if succeeded).

        Example:
            ```python
            ok = Ok("Hello, world!")
            print(await ok.map_or_else_await(int, len))  # 13

            error = Error("error!")
            print(await error.map_or_else_await(int, len))  # 0
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    def map_error(self, function: Unary[E, F]) -> Result[T, F]:
        """Maps [`Result[T, E]`][wraps.result.Result] to [`Result[T, F]`][wraps.result.Result]
        by applying the `function` to the contained [`Error[E]`][wraps.result.Error] value,
        leaving any [`Ok[T]`][wraps.result.Ok] untouched.

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

    @abstractmethod
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

    @abstractmethod
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
            default: The default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_error_or_else_await(self, default: AsyncNullary[F], function: Unary[E, F]) -> F:
        """Computes the default value (if succeeded), or applies `function`
        to the contained value (if errored).

        Example:
            ```python
            error = Error("error...")
            print(await error.map_error_or_else(int, len))  # 8

            ok = Ok("ok!")
            print(await ok.map_error_or_else(int, len))  # 0
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_await(self, function: AsyncUnary[T, U]) -> Result[U, E]:
        """Maps [`Result[T, E]`][wraps.result.Result] to [`Result[U, E]`][wraps.result.Result]
        by applying the asynchronous `function` to the contained [`Ok[T]`][wraps.result.Ok] value,
        leaving any [`Error[E]`][wraps.result.Error] untouched.

        This function can be used to compose the results of two functions.

        Example:
            ```python
            async def async_str(value: int) -> str:
                return str(value)

            value = 69
            mapped = "69"

            ok = Ok(value)

            assert await ok.map_await(async_str) == Ok(mapped)

            error = Error(0)

            assert await error.map_await(async_str) == error
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped result.
        """
        ...

    @abstractmethod
    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        """Returns the default value (if errored), or applies the asynchronous `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            ok = Ok("Hello, world!")
            print(await ok.map_await_or(42, async_len))  # 13

            error = Error("error...")
            print(error.map_await_or(42, async_len))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @abstractmethod
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
            default: The default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        """Computes the default value (if errored), or applies the asynchronous `function`
        to the contained value (if succeeded).

        Example:
            ```python
            async def default() -> int:
                return 0

            async def async_len(value: str) -> int:
                return len(value)

            ok = Ok("Hello, world!")
            print(await ok.map_await_or_else_await(default, async_len))  # 13

            error = Error("error!")
            print(await error.map_await_or_else_await(default, async_len))  # 0
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_error_await(self, function: AsyncUnary[E, F]) -> Result[T, F]:
        """Maps [`Result[T, E]`][wraps.result.Result] to [`Result[T, F]`][wraps.result.Result]
        by applying the asynchronous `function` to the contained [`Error[E]`][wraps.result.Error] value,
        leaving any [`Ok[T]`][wraps.result.Ok] untouched.

        Example:
            ```python
            async def async_str(value: int) -> str:
                return str(value)

            value = 42
            mapped = "42"

            error = Error(value)

            assert await error.map_error_await(async_str) == Error(mapped)

            ok = Ok(13)

            assert await ok.map_error_await(async_str) == ok
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped result.
        """
        ...

    @abstractmethod
    async def map_error_await_or(self, default: F, function: AsyncUnary[E, F]) -> F:
        """Returns the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            error = Error("Bye, world!")
            print(await error.map_error_await_or(42, async_len))  # 11

            ok = Ok("Hello, world!")
            print(await ok.map_error_await_or(42, async_len))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default value.
        """
        ...

    @abstractmethod
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
            default: The default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    async def map_error_await_or_else_await(
        self, default: AsyncNullary[F], function: AsyncUnary[E, F]
    ) -> F:
        """Computes the default value (if succeeded), or applies the asynchronous `function`
        to the contained value (if errored).

        Example:
            ```python
            async def default() -> int:
                return 0

            async def async_len(value: str) -> int:
                return len(value)

            error = Error("error")
            print(await error.map_error_await_or_else_await(default, async_len))  # 5

            ok = Ok("ok")
            print(await ok.map_error_await_or_else_await(default, async_len))  # 0
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @abstractmethod
    def iter(self) -> Iterator[T]:
        """Returns an iterator over the possibly contained value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> next(ok.iter())
            42

            >>> error = Error(0)
            >>> next(error.iter())
            Traceback (most recent call last):
              ...
            StopIteration
            ```

        Returns:
            An iterator over the possibly contained value.
        """
        ...

    @abstractmethod
    def iter_error(self) -> Iterator[E]:
        """Returns an iterator over the possibly contained error value.

        Example:
            ```python
            >>> error = Error(13)
            >>> next(error.iter_error())
            13

            >>> ok = Ok(1)
            >>> next(ok.iter_error())
            Traceback (most recent call last):
              ...
            StopIteration
            ```

        Returns:
            An iterator over the possibly contained error value.
        """
        ...

    @abstractmethod
    def async_iter(self) -> AsyncIterator[T]:
        """Returns an asynchronous iterator over the possibly contained
        [`Ok[T]`][wraps.result.Ok] value.

        Example:
            ```python
            >>> ok = Ok(42)
            >>> await anext(ok.async_iter())
            42

            >>> error = Error(13)
            >>> await anext(error.async_iter())
            Traceback (most recent call last):
              ...
            StopAsyncIteration
            ```

        Returns:
            An asynchronous iterator over the success value.
        """
        ...

    @abstractmethod
    def async_iter_error(self) -> AsyncIterator[E]:
        """Returns an asynchronous iterator over the possibly contained
        [`Error[E]`][wraps.result.Error] value.

        Example:
            ```python
            >>> error = Error(0)
            >>> await anext(error.async_iter_error())
            0

            >>> ok = Ok(13)
            >>> await anext(ok.async_iter_error())
            Traceback (most recent call last):
              ...
            StopAsyncIteration
            ```

        Returns:
            An asynchronous iterator over the error value.
        """
        ...

    @abstractmethod
    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        """Returns [`Error[E]`][wraps.result.Error] if the result
        is [`Error[E]`][wraps.result.Error], otherwise calls the `function`
        with the wrapped value and returns the result.

        This function is also known as *bind* in functional programming.

        Example:
            ```python
            def inverse(value: float) -> Result[float, str]:
                return Ok(1.0 / value) if value else Error("can not divide by zero")

            ok = Ok(2.0)
            print(ok.and_then(inverse).unwrap())  # 0.5

            zero = Ok(0.0)
            assert zero.and_then(inverse).is_error()

            error = Error()
            assert error.and_then(inverse).is_error()
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The bound result.
        """
        ...

    @abstractmethod
    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        """Returns [`Error[E]`][wraps.result.Error] if the result
        is [`Error[E]`][wraps.result.Error], otherwise calls the asynchronous `function`
        with the wrapped value and returns the result.

        Example:
            ```python
            async def inverse(value: float) -> Result[float, str]:
                return Ok(1.0 / value) if value else Error("can not divide by zero")

            ok = Ok(2.0)
            result = await ok.and_then_await(inverse)
            print(result.unwrap())  # 0.5

            zero = Ok(0.0)
            assert (await zero.and_then_await(inverse)).is_error()

            error = Error()
            assert (await error.and_then_await(inverse)).is_error()
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The bound result.
        """
        ...

    @abstractmethod
    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        """Returns [`Ok[T]`][wraps.result.Ok] if the result
        is [`Ok[T]`][wraps.result.Ok], otherwise calls the `function`
        with the wrapped error value and returns the result.

        Example:
            ```python
            def check_non_zero(value: int) -> Result[int, str]:
                return Ok(value) if value else Error("the value is zero")

            error = Error(13)

            print(error.or_else(check_non_zero).unwrap())  # 13

            zero = Error(0)
            assert zero.or_else(check_non_zero).is_error()

            ok = Ok(42)
            assert ok.or_else(check_non_zero).is_ok()
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The bound result.
        """
        ...

    @abstractmethod
    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        """Returns [`Ok[T]`][wraps.result.Ok] if the result
        is [`Ok[T]`][wraps.result.Ok], otherwise calls the asynchronous `function`
        with the wrapped error value and returns the result.

        Example:
            ```python
            async def check_non_zero(value: int) -> Result[int, str]:
                return Ok(value) if value else Error("the value is zero")

            error = Error(13)

            result = await error.or_else_await(check_non_zero)

            print(result.unwrap())  # 13

            zero = Error(0)
            assert (await zero.or_else_await(check_non_zero)).is_error()

            ok = Ok(42)
            assert (await ok.or_else_await(check_non_zero)).is_ok()
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The bound result.
        """
        ...

    def try_flatten(self: ResultProtocol[ResultProtocol[T, E], E]) -> Result[T, E]:
        """Flattens a [`Result[Result[T, E], E]`][wraps.result.Result]
        to [`Result[T, E]`][wraps.result.Result].

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
        to [`Result[T, E]`][wraps.result.Result].

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

    @abstractmethod
    def transpose(self: ResultProtocol[OptionProtocol[T], E]) -> Option[Result[T, E]]:
        """Transposes a result of an option into option of a result.
        This function maps [`Result[Option[T], E]`][wraps.result.Result] into
        [`Option[Result[T, E]]`][wraps.option.Option] in the following way:

        - [`Ok(Null())`][wraps.result.Ok] is mapped to [`Null()`][wraps.option.Null];
        - [`Ok(Some(value))`][wraps.result.Ok] is mapped to [`Some(Ok(value))`][wraps.option.Some];
        - [`Error(error)`][wraps.result.Error] is mapped to
          [`Some(Error(error))`][wraps.option.Some].

        Example:
            ```python
            result = Ok(Some(64))
            option = Some(Ok(64))

            assert result.transpose() == option
            ```

        Returns:
            The transposed option.
        """
        ...

    @abstractmethod
    def contains(self, value: U) -> bool:
        """Checks if the contained value is equal to `value`.

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
            Whether the contained value is equal to `value`.
        """
        ...

    @abstractmethod
    def contains_error(self, error: F) -> bool:
        """Checks if the contained error value is equal to `error`.

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
            Whether the contained error value is equal to `error`.
        """
        ...

    @abstractmethod
    def flip(self) -> Result[E, T]:
        """Converts [`Result[T, E]`][wraps.result.Result] to [`Result[E, T]`][wraps.result.Result].

        [`Ok(value)`][wraps.result.Ok] and [`Error(error)`][wraps.result.Error] get swapped to
        [`Error(value)`][wraps.result.Error] and [`Ok(error)`][wraps.result.Ok], respectively.

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

    @abstractmethod
    def into_ok_or_error(self: ResultProtocol[V, V]) -> V:
        """Returns the [`Ok[V]`][wraps.result.Ok] value if `self` is [`Ok[V]`][wraps.result.Ok],
        and the [`Error[V]`][wraps.result.Error] value if `self` is [`Error[V]`][wraps.result.Error].

        In other words, this function returns the value (of type `V`) of
        a [`Result[V, V]`][wraps.result.Result], regardless of whether or not that result
        is [`Ok[V]`][wraps.result.Ok] or [`Error[V]`][wraps.result.Error].

        Example:
            ```python
            result: Result[int, int] = Ok(69)

            print(result.into_ok_or_error())  # 69
            ```

        Returns:
            The contained value, regardless of whether or not it is an error one.
        """
        ...

    @property
    @abstractmethod
    def Q(self) -> T:
        ...


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

    def unwrap_or_raise(self, exception: AnyException) -> T:
        return self.value

    def unwrap_or_raise_with(self, function: Nullary[AnyException]) -> T:
        return self.value

    async def unwrap_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> T:
        return self.value

    def unwrap_error(self) -> Never:
        panic(UNWRAP_ERROR_ON_OK)

    def unwrap_error_or(self, default: F) -> F:
        return default

    def unwrap_error_or_else(self, default: Nullary[F]) -> F:
        return default()

    async def unwrap_error_or_else_await(self, default: AsyncNullary[F]) -> F:
        return await default()

    def unwrap_error_or_raise(self, exception: AnyException) -> Never:
        raise exception

    def unwrap_error_or_raise_with(self, function: Nullary[AnyException]) -> Never:
        raise function()

    async def unwrap_error_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> Never:
        raise await function()

    def ok(self) -> Some[T]:
        return Some(self.value)

    def error(self) -> Null:
        return Null()

    def inspect(self, function: Inspect[T]) -> Ok[T]:
        function(self.value)

        return self

    def inspect_error(self, function: Inspect[E]) -> Ok[T]:
        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Ok[T]:
        await function(self.value)

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
        yield self.value

    def iter_error(self) -> Iterator[Never]:
        return
        yield  # type: ignore

    async def async_iter(self) -> AsyncIterator[T]:
        yield self.value

    async def async_iter_error(self) -> AsyncIterator[Never]:
        return
        yield  # type: ignore

    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return function(self.value)

    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Result[U, E]:
        return await function(self.value)

    def or_else(self, function: Unary[E, Result[T, F]]) -> Ok[T]:
        return self

    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Ok[T]:
        return self

    @overload
    def transpose(self: Ok[Some[T]]) -> Some[Ok[T]]:
        ...

    @overload
    def transpose(self: Ok[Null]) -> Null:
        ...

    @overload
    def transpose(self: Ok[Option[T]]) -> Option[Ok[T]]:
        ...

    def transpose(self: Ok[Option[T]]) -> Option[Ok[T]]:
        option = self.value

        if is_some(option):
            return option.create(self.create(option.value))  # type: ignore

        return option  # type: ignore

    def contains(self, value: U) -> bool:
        return self.value == value

    def contains_error(self, error: F) -> Literal[False]:
        return False

    def flip(self, error_type: Optional[Type[Error[T]]] = None) -> Error[T]:
        if error_type is None:
            error_type = Error[T]

        return error_type(self.value)

    def into_ok_or_error(self: Ok[V]) -> V:
        return self.value

    @property
    def Q(self) -> T:
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

    def unwrap_or_raise(self, exception: AnyException) -> Never:
        raise exception

    def unwrap_or_raise_with(self, function: Nullary[AnyException]) -> Never:
        raise function()

    async def unwrap_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> Never:
        raise await function()

    def unwrap_error_or(self, default: F) -> E:
        return self.value

    def unwrap_error_or_else(self, default: Nullary[F]) -> E:
        return self.value

    async def unwrap_error_or_else_await(self, default: AsyncNullary[F]) -> E:
        return self.value

    def unwrap_error_or_raise(self, exception: AnyException) -> E:
        return self.value

    def unwrap_error_or_raise_with(self, function: Nullary[AnyException]) -> E:
        return self.value

    async def unwrap_error_or_raise_with_await(self, function: AsyncNullary[AnyException]) -> E:
        return self.value

    def inspect(self, function: Inspect[T]) -> Error[E]:
        return self

    def inspect_error(self, function: Inspect[E]) -> Error[E]:
        function(self.value)

        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Error[E]:
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
        return
        yield  # type: ignore

    def iter_error(self) -> Iterator[E]:
        yield self.value

    async def async_iter(self) -> AsyncIterator[Never]:
        return
        yield  # type: ignore

    async def async_iter_error(self) -> AsyncIterator[E]:
        yield self.value

    def and_then(self, function: Unary[T, Result[U, E]]) -> Error[E]:
        return self

    async def and_then_await(self, function: AsyncUnary[T, Result[U, E]]) -> Error[E]:
        return self

    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return function(self.value)

    async def or_else_await(self, function: AsyncUnary[E, Result[T, F]]) -> Result[T, F]:
        return await function(self.value)

    def transpose(self: Error[E], some_type: Type[Some[Error[E]]] = Some) -> Some[Error[E]]:
        return some_type(self)

    def contains(self, value: U) -> Literal[False]:
        return False

    def contains_error(self, error: F) -> bool:
        return self.value == error

    def flip(self, ok_type: Optional[Type[Ok[E]]] = None) -> Ok[E]:
        if ok_type is None:
            ok_type = Ok[E]

        return ok_type(self.value)

    def into_ok_or_error(self: Error[V]) -> V:
        return self.value

    @property
    def Q(self) -> Never:
        raise ResultShortcut(self.value)


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


ET = TypeVar("ET", bound=AnyException)
FT = TypeVar("FT", bound=AnyException)


@final
@frozen()
class WrapResult(Generic[ET]):
    """Wraps a `function` returning `T` into a function returning
    [`Result[T, ET]`][wraps.result.Result].

    This handles exceptions via returning [`Error(error)`][wraps.result.Error] on `error`,
    wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

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

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapResult[FT]:
        return cls(error_type)  # type: ignore

    def __call__(self, function: Callable[P, T]) -> Callable[P, Result[T, ET]]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, ET]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapResult[FT]:
        return self.create(error_type)


if TYPE_CHECKING:

    def wrap_result(function: Callable[P, T]) -> Callable[P, Result[T, Exception]]:
        """Wraps a `function` returning `T` into a function returning
        [`Result[T, ET]`][wraps.result.Result].

        By default `ET` is [`Exception`][Exception], so this function returns
        [`Result[T, Exception]`][wraps.result.Result] unless specified otherwise.

        This handles exceptions via returning [`Error(error)`][wraps.result.Error] on `error`,
        wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

        Example:
            ```python
            @wrap_result[ValueError]
            def parse(string: str) -> int:
                return int(string)

            assert parse("512").is_ok()
            assert parse("uwu").is_error()
            ```

        Arguments:
            function: The function to wrap.

        Returns:
            The wrapping function.
        """
        ...

else:
    wrap_result = WrapResult(Exception)


@final
@frozen()
class WrapResultAwait(Generic[ET]):
    """Wraps an asynchronous `function` returning `T` into an asynchronous function returning
    [`Result[T, ET]`][wraps.result.Result].

    This handles exceptions via returning [`Error(error)`][wraps.result.Error] on `error`,
    wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

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

    error_type: Type[ET]

    @classmethod
    def create(cls, error_type: Type[FT]) -> WrapResultAwait[FT]:
        return cls(error_type)  # type: ignore

    def __call__(
        self, function: Callable[P, Awaitable[T]]
    ) -> Callable[P, Awaitable[Result[T, ET]]]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, ET]:
            try:
                return Ok(await function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[FT]) -> WrapResultAwait[FT]:
        return self.create(error_type)


if TYPE_CHECKING:

    def wrap_result_await(
        function: Callable[P, Awaitable[T]]
    ) -> Callable[P, Awaitable[Result[T, Exception]]]:
        """Wraps an asynchronous `function` returning `T` into an asynchronous function returning
        [`Result[T, ET]`][wraps.result.Result].

        By default `ET` is [`Exception`][Exception], so this function returns
        [`Result[T, Exception]`][wraps.result.Result] unless specified otherwise.

        This handles exceptions via returning [`Error(error)`][wraps.result.Error] on `error`,
        wrapping the resulting `value` into [`Ok(value)`][wraps.result.Ok].

        Example:
            ```python
            @wrap_result_await[ValueError]
            async def parse(string: str) -> int:
                return int(string)

            assert (await parse("512")).is_ok()
            assert (await parse("uwu")).is_error()
            ```

        Arguments:
            function: The asynchronous function to wrap.

        Returns:
            The asynchronous wrapping function.
        """
        ...

else:
    wrap_result_await = WrapResultAwait(Exception)
