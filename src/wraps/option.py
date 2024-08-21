"""Optional values.

[`Option[T]`][wraps.option.Option] represents an optional value:
every [`Option[T]`][wraps.option.Option] is either [`Some[T]`][wraps.option.Some] and
contains a value, or [`Null`][wraps.option.Null], and does not.

[`Option[T]`][wraps.option.Option] types can be very common in python code,
as they have a number of uses:

- Initial values (see [`ReAwaitable[T]`][wraps.futures.reawaitable.ReAwaitable]);
- Return values for functions not defined over their entire input range (partial functions);
- Return value for otherwise reporting simple errors, where [`Null`][wraps.option.Null]
  is returned on error;
- Optional function arguments (albeit slightly unergonomic).

[`Option[T]`][wraps.option.Option] is commonly paired with pattern matching to query
the presence of [`Some[T]`][wraps.option.Some] value (`T`) and take action,
always accounting for the [`Null`][wraps.option.Null] case:

```python
# option.py

from wraps import NULL, Option, Some


def divide(numerator: float, denominator: float) -> Option[float]:
    return Some(numerator / denominator) if denominator else NULL
```

```python
from wraps import Null, Some

from option import divide

DIVISION_BY_ZERO = "division by zero"

match divide(1.0, 2.0):
    case Some(result):
        print(result)

    case Null():
        print(DIVISION_BY_ZERO)
```

Here, we know that [`Null`][wraps.option.Null] represents only one case,
that is, attempts to divide by zero. However, when we need to represent multiple errors
from one function, we might want to use [`Result[T, E]`][wraps.result.Result] instead,
as described in the [`result`][wraps.result] section.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
    overload,
)

from attrs import frozen
from funcs.decorators import wraps
from funcs.functions import identity
from typing_aliases import (
    AnyError,
    AsyncBinary,
    AsyncCallable,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Binary,
    Inspect,
    NormalError,
    Nullary,
    Predicate,
    Unary,
    required,
)
from typing_extensions import Never, ParamSpec, TypeIs

from wraps.errors import ErrorTypes
from wraps.iters import async_empty, async_once, empty, once
from wraps.panics import panic
from wraps.reprs import empty_repr, wrap_repr

__all__ = (
    # option
    "Option",
    "Some",
    "Null",
    "NULL",
    "is_some",
    "is_null",
    # optional
    "wrap_optional",
    # decorators
    "WrapOption",
    "WrapOptionAwait",
    "wrap_option_on",
    "wrap_option_await_on",
    "wrap_option",
    "wrap_option_await",
)

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E")


class OptionProtocol(AsyncIterable[T], Iterable[T], Protocol[T]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter()

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter()

    @required
    def is_some(self) -> bool:
        """Checks if the option is [`Some[T]`][wraps.option.Some].

        Example:
            ```python
            some = Some(42)
            assert some.is_some()

            null = NULL
            assert not null.is_some()
            ```

        Returns:
            Whether the option is [`Some[T]`][wraps.option.Some].
        """
        ...

    @required
    def is_some_and(self, predicate: Predicate[T]) -> bool:
        """Checks if the option is [`Some[T]`][wraps.option.Some] and the value
        inside of it matches the `predicate`.

        Example:
            ```python
            def is_positive(value: int) -> bool:
                return value > 0

            some = Some(13)
            assert some.is_some_and(is_positive)

            zero = Some(0)
            assert not zero.is_some_and(is_positive)

            null = NULL
            assert not null.is_some_and(is_positive)
            ```

        Arguments:
            predicate: The predicate to check the possibly contained value against.

        Returns:
            Whether the option is [`Some[T]`][wraps.option.Some] and the predicate is matched.
        """
        ...

    @required
    async def is_some_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        """Checks if the option is [`Some[T]`][wraps.option.Some] and the value
        inside of it matches the asynchronous `predicate`.

        Example:
            ```python
            async def is_negative(value: int) -> bool:
                return value < 0

            some = Some(-42)
            assert await some.is_some_and_await(is_negative)

            zero = Some(0)
            assert not await zero.is_some_and_await(is_negative)

            null = NULL
            assert not await null.is_some_and_await(is_negative)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the possibly contained value against.

        Returns:
            Whether the option is [`Some[T]`][wraps.option.Some] and
            the asynchronous predicate is matched.
        """
        ...

    @required
    def is_null(self) -> bool:
        """Checks if the option is [`Null`][wraps.option.Null].

        Example:
            ```python
            null = NULL
            assert null.is_null()

            some = Some(34)
            assert not some.is_null()
            ```

        Returns:
            Whether the option is [`Null`][wraps.option.Null].
        """
        ...

    @required
    def expect(self, message: str) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value.

        Example:
            ```python
            >>> some = Some(42)
            >>> some.expect("panic!")
            42
            >>> null = NULL
            >>> null.expect("panic!")
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: panic!
            ```

        Arguments:
            message: The message to use in panicking.

        Raises:
            Panic: Panics with the `message` if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    def extract(self) -> Optional[T]:
        """Returns the contained [`Some[T]`][wraps.option.Some] value or [`None`][None].

        Example:
            ```python
            >>> some = Some(42)
            >>> some.extract()
            42
            >>> null = NULL
            >>> null.extract()
            >>> # None
            ```

        Returns:
            The contained value or [`None`][None].
        """
        ...

    @required
    def unwrap(self) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value.

        Because this function may panic, its use is generally discouraged.

        Instead, prefer to use pattern matching and handle the [`Null`][wraps.option.Null]
        case explicitly, or call [`unwrap_or`][wraps.option.OptionProtocol.unwrap_or]
        or [`unwrap_or_else`][wraps.option.OptionProtocol.unwrap_or_else].

        Example:
            ```python
            >>> some = Some(42)
            >>> some.unwrap()
            42
            >>> null = NULL
            >>> null.unwrap()
            Traceback (most recent call last):
              ...
            wraps.panics.Panic: called `unwrap` on null
            ```

        Raises:
            Panic: Panics if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap_or(self, default: T) -> T:  # type: ignore[misc]
        """Returns the contained [`Some[T]`][wraps.option.Some] value or the provided `default`.

        Example:
            ```python
            some = Some(13)
            assert some.unwrap_or(0)

            null = NULL
            assert not null.unwrap_or(0)
            ```

        Arguments:
            default: The default value to use.

        Returns:
            The contained value or the `default` one.
        """
        ...

    @required
    def unwrap_or_else(self, default: Nullary[T]) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value or
        computes it from the `default` function.

        Example:
            ```python
            some = Some(13)
            assert some.unwrap_or_else(int)

            null = NULL
            assert not null.unwrap_or_else(int)
            ```

        Arguments:
            default: The default-computing function to use.

        Returns:
            The contained value or the `default()` one.
        """
        ...

    @required
    async def unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value
        or computes it from the asynchronous `default` function.

        Example:
            ```python
            async def default() -> int:
                return 0

            some = Some(42)
            assert await some.unwrap_or_else_await(default)

            null = NULL
            assert not await null.unwrap_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default-computing function to use.

        Returns:
            The contained value or the `await default()` one.
        """
        ...

    @required
    def or_raise(self, error: AnyError) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value
        or raises the `error` provided.

        Arguments:
            error: The error to raise if the option is [`Null`][wraps.option.Null].

        Raises:
            AnyError: The error provided, if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    def or_raise_with(self, error: Nullary[AnyError]) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value
        or raises the error computed from `error`.

        Arguments:
            error: The function computing the error to raise
                if the option is [`Null`][wraps.option.Null].

        Raises:
            AnyError: The error computed, if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    async def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value
        or raises the error computed asynchronously from `error`.

        Arguments:
            error: The asynchronous function computing the error to raise
                if the option is [`Null`][wraps.option.Null].

        Raises:
            AnyError: The error computed, if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    def inspect(self, function: Inspect[T]) -> Option[T]:
        """Inspects a possibly contained [`Option[T]`][wraps.option.Option] value.

        Example:
            ```python
            some = Some("Hello, world!")

            same = some.inspect(print)  # Hello, world!

            assert some == same
            ```

        Arguments:
            function: The inspecting function.

        Returns:
            The inspected option.
        """
        ...

    @required
    async def inspect_await(self, function: AsyncInspect[T]) -> Option[T]:
        """Inspects a possibly contained [`Option[T]`][wraps.option.Option] value.

        Example:
            ```python
            async def function(value: str) -> None:
                print(value)

            some = Some("Hello, world!")

            same = await some.inspect(function)  # Hello, world!

            assert some == same
            ```

        Arguments:
            function: The asynchronous inspecting function.

        Returns:
            The inspected option.
        """
        ...

    @required
    def map(self, function: Unary[T, U]) -> Option[U]:
        """Maps an [`Option[T]`][wraps.option.Option] to an [`Option[U]`][wraps.option.Option]
        by applying the `function` to the contained value.

        Example:
            ```python
            some = Some("Hello, world!")

            print(some.map(len).unwrap())  # 13
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The mapped option.
        """
        ...

    @required
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        """Returns the `default` value (if none), or applies the `function`
        to the contained value (if any).

        Example:
            ```python
            some = Some("nekit")

            print(some.map_or(42, len))  # 5

            null = NULL

            print(null.map_or(42, len))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The function to apply.

        Returns:
            The resulting value or the `default` one.
        """
        ...

    @required
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        """Computes the default value from the `default` function (if none),
        or applies the `function` to the contained value (if any).

        Example:
            ```python
            def default() -> int:
                return 42

            some = Some("Hello, world!")

            print(some.map_or_else(default, len))  # 13

            null = NULL

            print(null.map_or_else(default, len))  # 42
            ```

        Arguments:
            default: The default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting value or the `default()` one.
        """
        ...

    @required
    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        """Computes the default value from the asynchronous `default` function (if none),
        or applies the `function` to the contained value (if any).

        Example:
            ```python
            async def default() -> int:
                return 42

            some = Some("Hello, world!")

            print(await some.map_or_else_await(default, len))  # 13

            null = NULL

            print(await null.map_or_else_await(default, len))  # 42
            ```

        Arguments:
            default: The asynchronous default-computing function to use.
            function: The function to apply.

        Returns:
            The resulting value or the `await default()` one.
        """
        ...

    @required
    async def map_await(self, function: AsyncUnary[T, U]) -> Option[U]:
        """Maps an [`Option[T]`][wraps.option.Option] to an [`Option[U]`][wraps.option.Option]
        by applying the asynchronous `function` to the contained value.

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            some = Some("Hello, world!")

            mapped = await some.map_await(function)

            print(some.unwrap())  # 13
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The mapped option.
        """
        ...

    @required
    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        """Returns the `default` value (if none), or applies the asynchronous `function`
        to the contained value (if any).

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            some = Some("nekit")

            print(await some.map_await_or(42, function))  # 5

            null = NULL

            print(await null.map_await_or(42, function))  # 42
            ```

        Arguments:
            default: The default value to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting value or the `default` one.
        """
        ...

    @required
    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        """Computes the default value from the `default` function (if none),
        or applies the asynchronous `function` to the contained value (if any).

        Example:
            ```python
            async def function(value: str) -> int:
                return len(value)

            def default() -> int:
                return 0

            some = Some("Hello, world!")

            print(await some.map_await_or_else(default, function))  # 13

            null = NULL

            print(await null.map_await_or_else(default, function))  # 0
            ```

        Arguments:
            default: The default-computing function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting value or the `default()` one.
        """
        ...

    @required
    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        """Computes the default value (if none), or applies the asynchronous `function`
        to the contained value (if any).

        Example:
            ```python
            async def default() -> int:
                return 42

            async def function(value: str) -> int:
                return len(value)

            some = Some("Hello, world!")

            print(await some.map_await_or_else_await(default, function))  # 13

            null = NULL

            print(await null.map_await_or_else_await(default, function))  # 42
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting value or the `await default()` one.
        """
        ...

    @required
    def ok_or(self, error: E) -> Result[T, E]:
        """Transforms an [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Err(error)`][wraps.result.Err].

        Example:
            ```python
            error = 13

            some = Some(42)
            assert some.ok_or(error).is_ok()

            null = NULL
            assert null.ok_or(error).is_err()
            ```

        Arguments:
            error: The error to use.

        Returns:
            The transformed result.
        """
        ...

    @required
    def ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        """Transforms an [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Err(error())`][wraps.result.Err].

        Example:
            ```python
            def error() -> Err[int]:
                return Err(0)

            some = Some(7)
            assert some.ok_or_else(error).is_ok()

            null = NULL
            assert null.ok_or_else(error).is_err()
            ```

        Arguments:
            error: The error-computing function to use.

        Returns:
            The transformed result.
        """
        ...

    @required
    async def ok_or_else_await(self, error: AsyncNullary[E]) -> Result[T, E]:
        """Transforms an [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Err(await error())`][wraps.result.Err].

        Example:
            ```python
            async def error() -> Err[int]:
                return Err(0)

            some = Some(7)
            result = await some.ok_or_else_await(error)

            assert result.is_ok()

            null = NULL
            result = await null.ok_or_else_await(error)

            assert result.is_err()
            ```

        Arguments:
            error: The error-computing function to use.

        Returns:
            The transformed result.
        """
        ...

    @required
    def iter(self) -> Iterator[T]:
        """Returns an iterator over the possibly contained value.

        Example:
            ```python
            >>> some = Some(42)
            >>> next(some.iter(), 0)
            42
            >>> null = NULL
            >>> next(null.iter(), 0)
            0
            ```

        Returns:
            An iterator over the possible value.
        """
        ...

    @required
    def async_iter(self) -> AsyncIterator[T]:
        """Returns an asynchronous iterator over the possibly contained value.

        Example:
            ```python
            >>> some = Some(42)
            >>> await async_next(some.async_iter(), 0)
            42
            >>> null = NULL
            >>> await async_next(null.async_iter(), 0)
            0
            ```

        Returns:
            An asynchronous iterator over the possible value.
        """
        ...

    @required
    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        """Returns the option if it is [`Null`][wraps.option.Null],
        otherwise calls the `function` with the wrapped value and returns the result.

        This function is also known as *bind* in functional programming.

        Example:
            ```python
            def inverse(value: float) -> Option[float]:
                return Some(1.0 / value) if value else NULL

            some = Some(2.0)
            print(some.and_then(inverse).unwrap())  # 0.5

            zero = Some(0.0)
            assert zero.and_then(inverse).is_null()

            null = NULL
            assert null.and_then(inverse).is_null()
            ```

        Arguments:
            function: The function to apply.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Option[U]:
        """Returns the option if it is [`Null`][wraps.option.Null],
        otherwise calls the asynchronous `function` with the wrapped value and returns the result.

        Example:
            ```python
            async def inverse(value: float) -> Option[float]:
                return Some(1.0 / value) if value else NULL

            some = Some(2.0)
            option = await some.and_then_await(inverse)

            print(option.unwrap())  # 0.5

            zero = Some(0.0)
            option = await zero.and_then_await(inverse)

            assert option.is_null()

            null = NULL
            option = await null.and_then_await(inverse)

            assert option.is_null()
            ```

        Arguments:
            function: The asynchronous function to apply.

        Returns:
            The resulting option.
        """
        ...

    @required
    def filter(self, predicate: Predicate[T]) -> Option[T]:
        """Returns the option if it is [`Null`][wraps.option.Null],
        otherwise calls the `predicate` with the wrapped value and returns:

        - [`Some(value)`][wraps.option.Some] if the contained `value` matches the predicate, and
        - [`Null`][wraps.option.Null] otherwise.

        Example:
            ```python
            def is_even(value: int) -> bool:
                return not value % 2

            null = NULL
            assert null.filter(is_even).is_null()

            even = Some(2)
            assert even.filter(is_even).is_some()

            odd = Some(1)
            assert odd.filter(is_even).is_null()
            ```

        Arguments:
            predicate: The predicate to check the contained value against.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        """Returns the option if it is [`Null`][wraps.option.Null],
        otherwise calls the asynchronous `predicate` with the wrapped value and returns:

        - [`Some(value)`][wraps.option.Some] if the contained `value` matches the predicate, and
        - [`Null`][wraps.option.Null] otherwise.

        Example:
            ```python
            async def is_even(value: int) -> bool:
                return not value % 2

            null = NULL
            assert (await null.filter_await(is_even)).is_null()

            even = Some(2)
            assert (await even.filter_await(is_even)).is_some()

            odd = Some(1)
            assert (await odd.filter_await(is_even)).is_null()
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

        Returns:
            The resulting option.
        """
        ...

    @required
    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls
        the `default` function and returns the result.

        Example:
            ```python
            def default() -> Some[int]:
                return Some(13)

            some = Some(42)
            null = NULL

            assert some.or_else(default).is_some()
            assert null.or_else(default).is_some()
            ```

        Arguments:
            default: The default-computing function to use.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def or_else_await(self, default: AsyncNullary[Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls
        the asynchronous `default` function and returns the result.

        Example:
            ```python
            async def default() -> Some[int]:
                return Some(13)

            some = Some(42)
            null = NULL

            assert (await some.or_else_await(default)).is_some()
            assert (await null.or_else_await(default)).is_some()
            ```

        Arguments:
            default: The asynchronous default function to use.

        Returns:
            The resulting option.
        """
        ...

    @required
    def xor(self, option: Option[T]) -> Option[T]:
        """Returns [`Some[T]`][wraps.option.Some] if exactly one of `self` and `option`
        is [`Some[T]`][wraps.option.Option], otherwise returns [`Null`][wraps.option.Null].

        Example:
            ```python
            some = Some(69)
            other = Some(7)

            null = NULL

            assert some.xor(other) == null
            assert null.xor(other) == other
            assert some.xor(null) == some
            assert null.xor(null) == null
            ```

        Arguments:
            option: The option to *xor* `self` with.

        Returns:
            The resulting option.
        """
        ...

    @required
    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        """Zips `self` with an `option`.

        If `self` is [`Some(s)`][wraps.option.Some] and `option` is [`Some(o)`][wraps.option.Some],
        this method returns [`Some((s, o))`][wraps.option.Some]. Otherwise,
        [`Null`][wraps.option.Null] is returned.

        Example:
            ```python
            x = 0.7
            y = 1.3

            some_x = Some(x)
            some_y = Some(y)

            some_tuple = Some((x, y))

            assert some_x.zip(some_y) == some_point

            null = NULL

            assert some_y.zip(null) == null
            ```

        Arguments:
            option: The option to *zip* `self` with.

        Returns:
            The resulting option.
        """
        ...

    @required
    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        """Zips `self` with an `option` using `function`.

        If `self` is [`Some(s)`][wraps.option.Some] and `option` is [`Some(o)`][wraps.option.Some],
        this method returns [`Some(function(s, o))`][wraps.option.Some]. Otherwise,
        [`Null`][wraps.option.Null] is returned.

        Example:
            ```python
            @frozen()
            class Point:
                x: float
                y: float

            x = 1.3
            y = 4.2

            some_x = Some(x)
            some_y = Some(y)

            some_point = Some(Point(x, y))

            assert some_x.zip_with(some_y, Point) == some_point

            null = NULL

            assert some_x.zip_with(null, Point) == null
            ```

        Arguments:
            option: The option to *zip* `self` with.
            function: The function to use for zipping.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def zip_with_await(self, option: Option[U], function: AsyncBinary[T, U, V]) -> Option[V]:
        """Zips `self` with an `option` using asynchronous `function`.

        If `self` is [`Some(s)`][wraps.option.Some] and `option` is [`Some(o)`][wraps.option.Some],
        this method returns [`Some(await function(s, o))`][wraps.option.Some]. Otherwise,
        [`Null`][wraps.option.Null] is returned.

        Example:
            ```python
            @frozen()
            class Point:
                x: float
                y: float

            async def point(x: float, y: float) -> Point:
                return Point(x, y)

            x = 1.3
            y = 4.2

            some_x = Some(x)
            some_y = Some(y)

            some_point = Some(Point(x, y))

            assert await some_x.zip_with(some_y, point) == some_point

            null = NULL

            assert await some_x.zip_with(null, point) == null
            ```

        Arguments:
            option: The option to *zip* `self` with.
            function: The asynchronous function to use for zipping.

        Returns:
            The resulting option.
        """
        ...

    @required
    def unzip(self: OptionProtocol[Tuple[U, V]]) -> Tuple[Option[U], Option[V]]:
        """Unzips an option into two options.

        If `self` is [`Some((u, v))`][wraps.option.Some], this method returns
        ([`Some(u)`][wraps.option.Some], [`Some(v)`][wraps.option.Some]) tuple.
        Otherwise, ([`Null`][wraps.option.Null], [`Null`][wraps.option.Null]) is returned.

        Example:
            ```python
            value = 13
            other = 42

            zipped = Some((value, other))

            assert zipped.unzip() == (Some(value), Some(other))

            null = NULL

            assert null.unzip() == (NULL, NULL)

        Returns:
            The resulting tuple of two options.
        """
        ...

    def flatten(self: OptionProtocol[OptionProtocol[U]]) -> Option[U]:
        """Flattens an [`Option[Option[T]]`][wraps.option.Option]
        to [`Option[T]`][wraps.option.Option].

        Example:
            ```python
            some = Some(42)
            some_nested = Some(some)
            assert some_nested.flatten() == some

            null = NULL
            null_nested = Some(null)
            assert null_nested.flatten() == null

            assert null.flatten() == null
            ```

        Returns:
            The flattened option.
        """
        return self.and_then(identity)  # type: ignore[arg-type]

    @required
    def contains(self, value: U) -> bool:
        """Checks if the contained value (if any) is equal to `value`.

        Example:
            ```python
            value = 42
            other = 69

            some = Some(value)
            assert some.contains(value)
            assert not some.contains(other)

            null = NULL
            assert not null.contains(value)
            ```

        Arguments:
            value: The value to check against.

        Returns:
            Whether the contained value is equal to `value`.
        """
        ...

    @required
    def early(self) -> T:
        """Functionally similar to the *question-mark* (`?`) operator in Rust.

        Calls to this method are to be combined with
        [`@early_option`][wraps.early.decorators.early_option] decorators to work properly.
        """
        ...


UNWRAP_ON_NULL = "called `unwrap` on null"


@final
@frozen()
class Null(OptionProtocol[Never]):
    """The [`Null`][wraps.option.Null] variant of [`Option[T]`][wraps.option.Option]."""

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return empty_repr(self)

    @classmethod
    def create(cls) -> Null:
        return cls()

    def is_some(self) -> Literal[False]:
        return False

    def is_some_and(self, predicate: Predicate[T]) -> Literal[False]:
        return False

    async def is_some_and_await(self, predicate: AsyncPredicate[T]) -> Literal[False]:
        return False

    def is_null(self) -> Literal[True]:
        return True

    def expect(self, message: str) -> Never:
        panic(message)

    def extract(self) -> None:
        return None

    def unwrap(self) -> Never:
        panic(UNWRAP_ON_NULL)

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

    def inspect(self, function: Inspect[T]) -> Null:
        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Null:
        return self

    def map(self, function: Unary[T, U]) -> Null:
        return self

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return default

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return default()

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return await default()

    async def map_await(self, function: AsyncUnary[T, U]) -> Null:
        return self

    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return default

    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return default()

    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await default()

    def ok_or(self, error: E) -> Err[E]:
        return Err(error)

    def ok_or_else(self, error: Nullary[E]) -> Err[E]:
        return Err(error())

    async def ok_or_else_await(self, error: AsyncNullary[E]) -> Err[E]:
        return Err(await error())

    def iter(self) -> Iterator[Never]:
        return empty()

    def async_iter(self) -> AsyncIterator[Never]:
        return async_empty()

    def and_then(self, function: Unary[T, Option[U]]) -> Null:
        return self

    async def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Null:
        return self

    def filter(self, predicate: Predicate[T]) -> Null:
        return self

    async def filter_await(self, predicate: AsyncPredicate[T]) -> Null:
        return self

    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        return default()

    async def or_else_await(self, default: AsyncNullary[Option[T]]) -> Option[T]:
        return await default()

    def xor(self, option: Option[T]) -> Option[T]:
        return option

    def zip(self, option: Option[U]) -> Null:
        return self

    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Null:
        return self

    async def zip_with_await(self, option: Option[U], function: AsyncBinary[T, U, V]) -> Null:
        return self

    def unzip(self) -> Tuple[Null, Null]:
        return self, self

    def contains(self, value: U) -> Literal[False]:
        return False

    def early(self) -> Never:
        raise EarlyOption()


@final
@frozen()
class Some(OptionProtocol[T]):
    """[`Some[T]`][wraps.option.Some] variant of [`Option[T]`][wraps.option.Option]."""

    value: T

    def __repr__(self) -> str:
        return wrap_repr(self, self.value)

    @classmethod
    def create(cls, value: U) -> Some[U]:
        return cls(value)  # type: ignore[arg-type, return-value]

    def is_some(self) -> Literal[True]:
        return True

    def is_some_and(self, predicate: Predicate[T]) -> bool:
        return predicate(self.value)

    async def is_some_and_await(self, predicate: AsyncPredicate[T]) -> bool:
        return await predicate(self.value)

    def is_null(self) -> Literal[False]:
        return False

    def expect(self, message: str) -> T:
        return self.value

    def extract(self) -> T:
        return self.value

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:  # type: ignore[misc]
        return self.value

    def unwrap_or_else(self, default: Nullary[T]) -> T:
        return self.value

    def or_raise(self, error: AnyError) -> T:
        return self.value

    def or_raise_with(self, error: Nullary[AnyError]) -> T:
        return self.value

    async def or_raise_with_await(self, error: AsyncNullary[AnyError]) -> T:
        return self.value

    async def unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        return self.value

    def inspect(self, function: Inspect[T]) -> Some[T]:
        function(self.value)

        return self

    async def inspect_await(self, function: AsyncInspect[T]) -> Some[T]:
        await function(self.value)

        return self

    def map(self, function: Unary[T, U]) -> Some[U]:
        return self.create(function(self.value))

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return function(self.value)

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    async def map_await(self, function: AsyncUnary[T, U]) -> Some[U]:
        return self.create(await function(self.value))

    async def map_await_or(self, default: U, function: AsyncUnary[T, U]) -> U:
        return await function(self.value)

    async def map_await_or_else(self, default: Nullary[U], function: AsyncUnary[T, U]) -> U:
        return await function(self.value)

    async def map_await_or_else_await(
        self, default: AsyncNullary[U], function: AsyncUnary[T, U]
    ) -> U:
        return await function(self.value)

    def ok_or(self, error: E) -> Ok[T]:
        return Ok(self.value)

    def ok_or_else(self, error: Nullary[E]) -> Ok[T]:
        return Ok(self.value)

    async def ok_or_else_await(self, error: AsyncNullary[E]) -> Ok[T]:
        return Ok(self.value)

    def iter(self) -> Iterator[T]:
        return once(self.value)

    def async_iter(self) -> AsyncIterator[T]:
        return async_once(self.value)

    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        return function(self.value)

    async def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Option[U]:
        return await function(self.value)

    def filter(self, predicate: Predicate[T]) -> Option[T]:
        return self if predicate(self.value) else NULL

    async def filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        return self if await predicate(self.value) else NULL

    def or_else(self, default: Nullary[Option[T]]) -> Some[T]:
        return self

    async def or_else_await(self, default: AsyncNullary[Option[T]]) -> Some[T]:
        return self

    def xor(self, option: Option[T]) -> Option[T]:
        return self if is_null(option) else NULL

    @overload
    def zip(self, option: Null) -> Null: ...

    @overload
    def zip(self, option: Some[U]) -> Some[Tuple[T, U]]: ...

    @overload
    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]: ...

    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        return self.create((self.value, option.value)) if is_some(option) else NULL

    @overload
    def zip_with(self, option: Null, function: Binary[T, U, V]) -> Null: ...

    @overload
    def zip_with(self, option: Some[U], function: Binary[T, U, V]) -> Some[V]: ...

    @overload
    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]: ...

    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        return self.create(function(self.value, option.value)) if is_some(option) else NULL

    @overload
    async def zip_with_await(self, option: Null, function: AsyncBinary[T, U, V]) -> Null: ...

    @overload
    async def zip_with_await(self, option: Some[U], function: AsyncBinary[T, U, V]) -> Some[V]: ...

    @overload
    async def zip_with_await(
        self, option: Option[U], function: AsyncBinary[T, U, V]
    ) -> Option[V]: ...

    async def zip_with_await(self, option: Option[U], function: AsyncBinary[T, U, V]) -> Option[V]:
        return self.create(await function(self.value, option.value)) if is_some(option) else NULL

    def unzip(self: Some[Tuple[U, V]]) -> Tuple[Some[U], Some[V]]:
        u, v = self.value

        return self.create(u), self.create(v)

    def contains(self, value: U) -> bool:
        return self.value == value

    def early(self) -> T:
        return self.value


Option = Union[Some[T], Null]
"""Optional value, expressed as the union of [`Some[T]`][wraps.option.Some]
and [`Null`][wraps.option.Null].
"""

NULL = Null()
"""The instance of [`Null`][wraps.option.Null]."""


def is_some(option: Option[T]) -> TypeIs[Some[T]]:
    """This is the same as [`Option.is_some`][wraps.option.OptionProtocol.is_some],
    except it works as a *type guard*.
    """
    return option.is_some()


def is_null(option: Option[T]) -> TypeIs[Null]:
    """This is the same as [`Option.is_null`][wraps.option.OptionProtocol.is_null],
    except it works as a *type guard*.
    """
    return option.is_null()


def wrap_optional(optional: Optional[T]) -> Option[T]:
    """Wraps [`Optional[T]`][typing.Optional] into [`Option[T]`][wraps.option.Option].

    If the argument is [`None`][None], [`NULL`][wraps.option.NULL] is returned.
    Otherwise the `value` (of type `T`) is wrapped into [`Some(value)`][wraps.option.Some].

    Arguments:
        optional: The optional value to wrap.

    Returns:
        The wrapped option.
    """
    return NULL if optional is None else Some(optional)


# import cycle solution

from wraps.early.errors import EarlyOption
from wraps.result import Err, Ok, Result

if TYPE_CHECKING:
    from wraps.typing import OptionAsyncCallable, OptionCallable

P = ParamSpec("P")

A = TypeVar("A", bound=AnyError)


@final
@frozen()
class WrapOption(Generic[A]):
    """Wraps functions returning `T` into functions returning
    [`Option[T]`][wraps.option.Option].

    Errors are handled via returning [`NULL`][wraps.option.NULL] on `error` of
    [`error_types`][wraps.option.WrapOption.error_types], wrapping the resulting
    `value` into [`Some(value)`][wraps.option.Some].
    """

    error_types: ErrorTypes[A]
    """The error types to handle. See [`ErrorTypes[A]`][wraps.errors.ErrorTypes]."""

    def __call__(self, function: Callable[P, T]) -> OptionCallable[P, T]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(function(*args, **kwargs))

            except self.error_types.extract():
                return NULL

        return wrap


def wrap_option_on(head: Type[A], *tail: Type[A]) -> WrapOption[A]:
    """Creates [`WrapOption[A]`][wraps.option.WrapOption] decorators.

    This function enforces at least one error type to be provided.

    Example:
        ```python
        @wrap_option_on(ValueError)
        def parse(string: str) -> int:
            return int(string)

        assert parse("256").is_some()
        assert parse("uwu").is_null()
        ```

    Arguments:
        head: The head of the error types to handle.
        *tail: The tail of the error types to handle.

    Returns:
        The [`WrapOption[A]`][wraps.option.WrapOption] decorator created.
    """
    return WrapOption(ErrorTypes[A].from_head_and_tail(head, *tail))


wrap_option = wrap_option_on(NormalError)
"""An instance of [`WrapOption[NormalError]`][wraps.option.WrapOption]
(see [`NormalError`][typing_aliases.NormalError]).
"""


@final
@frozen()
class WrapOptionAwait(Generic[A]):
    """Wraps asynchronous functions returning `T` into functions returning
    [`Option[T]`][wraps.option.Option].

    Errors are handled via returning [`NULL`][wraps.option.NULL] on `error` of
    [`error_types`][wraps.option.WrapOptionAwait.error_types], wrapping the resulting
    `value` into [`Some(value)`][wraps.option.Some].
    """

    error_types: ErrorTypes[A]
    """The error types to handle. See [`ErrorTypes[A]`][wraps.errors.ErrorTypes]."""

    def __call__(self, function: AsyncCallable[P, T]) -> OptionAsyncCallable[P, T]:
        @wraps(function)
        async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
            try:
                return Some(await function(*args, **kwargs))

            except self.error_types.extract():
                return NULL

        return wrap


def wrap_option_await_on(head: Type[A], *tail: Type[A]) -> WrapOptionAwait[A]:
    """Creates [`WrapOptionAwait[A]`][wraps.option.WrapOptionAwait] decorators.

    This function enforces at least one error type to be provided.

    Example:
        ```python
        @wrap_option_await_on(ValueError)
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_some()
        assert (await parse("uwu")).is_null()
        ```

    Arguments:
        head: The head of the error types to handle.
        *tail: The tail of the error types to handle.

    Returns:
        The [`WrapOptionAwait[A]`][wraps.option.WrapOptionAwait] decorator created.
    """
    return WrapOptionAwait(ErrorTypes[A].from_head_and_tail(head, *tail))


wrap_option_await = wrap_option_await_on(NormalError)
"""An instance of [`WrapOptionAwait[NormalError]`][wraps.option.WrapOptionAwait]
(see [`NormalError`][typing_aliases.NormalError]).
"""
