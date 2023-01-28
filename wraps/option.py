"""Optional values.

[`Option[T]`][wraps.option.Option] represents an optional value:
every [`Option[T]`][wraps.option.Option] is either [`Some[T]`][wraps.option.Some] and
contains a value (of type `T`), or [`Null`][wraps.option.Null], and does not.

[`Option[T]`][wraps.option.Option] types can be very common in python code,
as they have a number of uses:

- Initial values (see [`ReAwaitable[T]`][wraps.future.ReAwaitable]);
- Return values for functions not defined over their entire input range (partial functions);
- Return value for otherwise reporting simple errors, where [`Null`][wraps.option.Null]
  is returned on error;
- Optional function arguments.

[`Option[T]`][wraps.option.Option] is commonly paired with pattern matching to query
the presence of [`Some[T]`][wraps.option.Some] value (`T`) and take action,
always accounting for the [`Null`][wraps.option.Null] case:

```python
from wraps import wrap_option

@wrap_option
def divide(numerator: float, denominator: float) -> float:
    return numerator / denominator
```

```python
from wraps import Null, Some

CAN_NOT_DIVIDE_BY_ZERO = "can not divide by zero"

option = divide(1.0, 2.0)

match option:
    case Some(result):
        print(result)

    case Null():
        print(CAN_NOT_DIVIDE_BY_ZERO)
```
"""

from __future__ import annotations

from abc import abstractmethod as required
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    Union,
    final,
    overload,
)

from attrs import frozen
from typing_extensions import Literal, Never, ParamSpec, Protocol, TypeGuard

from wraps.errors import EarlyOption, panic
from wraps.typing import (
    AsyncBinary,
    AsyncInspect,
    AsyncNullary,
    AsyncPredicate,
    AsyncUnary,
    Binary,
    Inspect,
    Nullary,
    Predicate,
    Unary,
)
from wraps.utils import identity

__all__ = (
    "Option",
    "Some",
    "Null",
    "is_some",
    "is_null",
    "wrap_option",
    "wrap_option_await",
    "wrap_optional",
)

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E")


class OptionProtocol(Protocol[T]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter().unwrap()

    def __aiter__(self) -> AsyncIterator[T]:
        return self.async_iter().unwrap()

    @required
    def is_some(self) -> bool:
        """Checks if the option is [`Some[T]`][wraps.option.Some].

        Example:
            ```python
            some = Some(42)
            assert some.is_some()

            null = Null()
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

            null = Null()
            assert not null.is_some_and(is_positive)
            ```

        Arguments:
            predicate: The predicate to check the contained value against.

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

            null = Null()
            assert not await null.is_some_and_await(is_negative)
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value against.

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
            null = Null()
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
            >>> null = Null()
            >>> null.expect("panic!")
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: panic!
            ```

        Arguments:
            message: The message used in panicking.

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

            >>> null = Null()
            >>> null.extract()
            >>>
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

            >>> null = Null()
            >>> null.unwrap()
            Traceback (most recent call last):
              ...
            wraps.errors.Panic: called `unwrap` on null
            ```

        Raises:
            Panic: Panics if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @required
    def unwrap_or(self, default: T) -> T:  # type: ignore
        """Returns the contained [`Some[T]`][wraps.option.Some] value or a provided default.

        Example:
            ```python
            default = 0

            some = Some(13)
            assert some.unwrap_or(default)

            null = Null()
            assert not null.unwrap_or(default)
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
        computes it from the function.

        Example:
            ```python
            some = Some(13)
            assert some.unwrap_or_else(int)

            null = Null()
            assert not null.unwrap_or_else(int)
            ```

        Arguments:
            default: The default function to use.

        Returns:
            The contained value or the `default()` one.
        """
        ...

    @required
    async def unwrap_or_else_await(self, default: AsyncNullary[T]) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value
        or computes it from the asynchronous function.

        Example:
            ```python
            async def default() -> int:
                return 0

            some = Some(42)
            assert await some.unwrap_or_else_await(default)

            null = Null()
            assert not await null.unwrap_or_else_await(default)
            ```

        Arguments:
            default: The asynchronous default function to use.

        Returns:
            The contained value or the `await default()` one.
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
        """Maps an [`Option[T]`][wraps.option.Option] to [`Option[U]`][wraps.option.Option]
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
        """Returns the default value (if none), or applies the `function`
        to the contained value (if any).

        Example:
            ```python
            some = Some("nekit")

            print(some.map_or(42, len))  # 5

            null = Null()

            print(null.map_or(42, len))  # 42
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
        """Computes the default value (if none), or applies the `function`
        to the contained value (if any).

        Example:
            ```python
            def default() -> int:
                return 42

            some = Some("Hello, world!")

            print(some.map_or_else(default, len))  # 13

            null = Null()

            print(null.map_or_else(default, len))  # 42
            ```

        Arguments:
            default: The default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    async def map_or_else_await(self, default: AsyncNullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if none), or applies the `function`
        to the contained value (if any).

        Example:
            ```python
            async def default() -> int:
                return 42

            some = Some("Hello, world!")

            print(await some.map_or_else_await(default, len))  # 13

            null = Null()

            print(await null.map_or_else_await(default, len))  # 42
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    async def map_await(self, function: AsyncUnary[T, U]) -> Option[U]:
        """Maps an [`Option[T]`][wraps.option.Option] to [`Option[U]`][wraps.option.Option]
        by applying the asynchronous `function` to the contained value.

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            some = Some("Hello, world!")

            mapped = await some.map_await(async_len)

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
        """Returns the default value (if none), or applies the asynchronous `function`
        to the contained value (if any).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            some = Some("nekit")

            print(await some.map_await_or(42, async_len))  # 5

            null = Null()

            print(await null.map_await_or(42, async_len))  # 42
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
        """Computes the default value (if none), or applies the asynchronous `function`
        to the contained value (if any).

        Example:
            ```python
            async def async_len(value: str) -> int:
                return len(value)

            some = Some("Hello, world!")

            print(await some.map_await_or_else(int, async_len))  # 13

            null = Null()

            print(await null.map_await_or_else(int, async_len))  # 0
            ```

        Arguments:
            default: The default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
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

            async def async_len(value: str) -> int:
                return len(value)

            some = Some("Hello, world!")

            print(await some.map_await_or_else_await(default, async_len))  # 13

            null = Null()

            print(await null.map_await_or_else_await(default, async_len))  # 42
            ```

        Arguments:
            default: The asynchronous default function to use.
            function: The asynchronous function to apply.

        Returns:
            The resulting or the default computed value.
        """
        ...

    @required
    def ok_or(self, error: E) -> Result[T, E]:
        """Transforms an [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Error(error)`][wraps.result.Error].

        Example:
            ```python
            error = Error(13)

            some = Some(42)
            assert some.ok_or(error).is_ok()

            null = Null()
            assert null.ok_or(error).is_error()
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
        to [`Error(error())`][wraps.result.Error].

        Example:
            ```python
            def error() -> Error[int]:
                return Error(0)

            some = Some(7)
            assert some.ok_or_else(error).is_ok()

            null = Null()
            assert null.ok_or_else(error).is_error()
            ```

        Arguments:
            error: The error function to use.

        Returns:
            The transformed result.
        """
        ...

    @required
    async def ok_or_else_await(self, error: AsyncNullary[E]) -> Result[T, E]:
        """Transforms an [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Error(await error())`][wraps.result.Error].

        Example:
            ```python
            async def error() -> Error[int]:
                return Error(0)

            some = Some(7)
            result = await some.ok_or_else_await(error)

            assert result.is_ok()

            null = Null()
            result = await null.ok_or_else_await(error)

            assert result.is_error()
            ```

        Arguments:
            error: The error function to use.

        Returns:
            The transformed result.
        """
        ...

    @required
    def iter(self) -> Iter[T]:
        """Returns an iterator over the possibly contained value.

        Example:
            ```python
            >>> some = Some(42)
            >>> next(some.iter())
            42

            >>> null = Null()
            >>> next(null.iter())
            Traceback (most recent call last):
              ...
            StopIteration
            ```

        Returns:
            An iterator over the possible value.
        """
        ...

    @required
    def async_iter(self) -> AsyncIter[T]:
        """Returns an asynchronous iterator over the possibly contained value.

        Example:
            ```python
            >>> some = Some(42)
            >>> await anext(some.async_iter())
            42

            >>> null = Null()
            >>> await anext(null.async_iter())
            Traceback (most recent call last):
              ...
            StopAsyncIteration
            ```

        Returns:
            An asynchronous iterator over the possible value.
        """
        ...

    @required
    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls the `function` with the wrapped value and returns the result.

        This function is also known as *bind*.

        Example:
            ```python
            def inverse(value: float) -> Option[float]:
                return Some(1.0 / value) if value else Null()

            some = Some(2.0)
            print(some.and_then(inverse).unwrap())  # 0.5

            zero = Some(0.0)
            assert zero.and_then(inverse).is_null()

            null = Null()
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
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls the asynchronous `function` with the wrapped value and returns the result.

        Example:
            ```python
            async def inverse(value: float) -> Option[float]:
                return Some(1.0 / value) if value else Null()

            some = Some(2.0)
            option = await some.and_then_await(inverse)

            print(option.unwrap())  # 0.5

            zero = Some(0.0)
            option = await zero.and_then_await(inverse)

            assert option.is_null()

            null = Null()
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
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls the `predicate` with the wrapped value and returns:

        - [`Some(value)`][wraps.option.Some] if the contained `value` matches the predicate, and
        - [`Null`][wraps.option.Null] otherwise.

        Example:
            ```python
            def is_even(value: int) -> bool:
                return not value % 2

            null = Null()
            assert null.filter(is_even).is_null()

            even = Some(2)
            assert even.filter(is_even).is_some()

            odd = Some(1)
            assert odd.filter(is_even).is_null()
            ```

        Arguments:
            predicate: The predicate to check the contained value with.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls the asynchronous `predicate` with the wrapped value and returns:

        - [`Some(value)`][wraps.option.Some] if the contained `value` matches the predicate, and
        - [`Null`][wraps.option.Null] otherwise.

        Example:
            ```python
            async def is_even(value: int) -> bool:
                return not value % 2

            null = Null()
            assert (await null.filter_await(is_even)).is_null()

            even = Some(2)
            assert (await even.filter_await(is_even)).is_some()

            odd = Some(1)
            assert (await odd.filter_await(is_even)).is_null()
            ```

        Arguments:
            predicate: The asynchronous predicate to check the contained value with.

        Returns:
            The resulting option.
        """
        ...

    @required
    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls
        the `default` and returns the result.

        Example:
            ```python
            def default() -> Null:
                return Null()

            some = Some(42)
            null = Null()

            assert some.or_else(default).is_some()
            assert null.or_else(default).is_null()
            ```

        Arguments:
            default: The default function to use.

        Returns:
            The resulting option.
        """
        ...

    @required
    async def or_else_await(self, default: AsyncNullary[Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls
        the asynchronous `default` and returns the result.

        Example:
            ```python
            async def default() -> Null:
                return Null()

            some = Some(42)
            null = Null()

            assert (await some.or_else_await(default)).is_some()
            assert (await null.or_else_await(default)).is_null()
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

            null = Null()

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

            null = Null()

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

            null = Null()

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

            null = Null()

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

            null = Null()

            assert null.unzip() == (Null(), Null())

        Returns:
            The resulting tuple of two options.
        """
        ...

    # @required
    # def transpose(self: OptionProtocol[ResultProtocol[T, E]]) -> Result[Option[T], E]:
    #     """Transposes an option of a result into result of an option.
    #     This function maps [`Option[Result[T, E]]`][wraps.option.Option] into
    #     [`Result[Option[T], E]]`][wraps.result.Result] in the following way:

    #     - [`Null()`][wraps.option.Null] is mapped to [`Ok(Null())`][wraps.result.Ok];
    #     - [`Some(Ok(value))`][wraps.option.Some] is mapped to
    #       [`Ok(Some(value))`][wraps.result.Ok];
    #     - [`Some(Error(error))`][wraps.option.Some] is mapped to
    #       [`Error(Some(error))`][wraps.result.Error].

    #     Example:
    #         ```python
    #         option = Some(Ok(7))
    #         result = Ok(Some(7))

    #         assert option.transpose() == result
    #         ```

    #     Returns:
    #         The transposed result.
    #     """
    #     ...

    def flatten(self: OptionProtocol[OptionProtocol[U]]) -> Option[U]:
        """Flattens an [`Option[Option[T]]`][wraps.option.Option]
        to [`Option[T]`][wraps.option.Option].

        Example:
            ```python
            some = Some(42)
            some_nested = Some(some)
            assert some_nested.flatten() == some

            null = Null()
            null_nested = Some(null)
            assert null_nested.flatten() == null

            assert null.flatten() == null
            ```

        Returns:
            The flattened option.
        """
        return self.and_then(identity)  # type: ignore

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

            null = Null()
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
        """Functionally similar to `?` operator in Rust.

        See [early](/reference/early) for more information.
        """
        ...


UNWRAP_ON_NULL = "called `unwrap` on null"


@final
@frozen()
class Null(OptionProtocol[Never]):
    """The [`Null`][wraps.option.Null] variant of [`Option[T]`][wraps.option.Option]."""

    def __bool__(self) -> Literal[False]:
        return False

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

    def ok_or(self, error: E) -> Error[E]:
        return Error(error)

    def ok_or_else(self, error: Nullary[E]) -> Error[E]:
        return Error(error())

    async def ok_or_else_await(self, error: AsyncNullary[E]) -> Error[E]:
        return Error(await error())

    def iter(self) -> Iter[Never]:
        return iter(self.actual_iter())

    def async_iter(self) -> AsyncIter[Never]:
        return async_iter(self.actual_async_iter())

    def actual_iter(self) -> Iterator[Never]:
        return
        yield  # type: ignore

    async def actual_async_iter(self) -> AsyncIterator[Never]:
        return
        yield  # type: ignore

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

    def __iter__(self) -> Iterator[T]:
        return self.iter()

    @classmethod
    def create(cls, value: U) -> Some[U]:
        return cls(value)  # type: ignore

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

    def unwrap_or(self, default: T) -> T:  # type: ignore
        return self.value

    def unwrap_or_else(self, default: Nullary[T]) -> T:
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

    def iter(self) -> Iter[T]:
        return iter(self.actual_iter())

    def async_iter(self) -> AsyncIter[T]:
        return async_iter(self.actual_async_iter())

    def actual_iter(self) -> Iterator[T]:
        yield self.value

    async def actual_async_iter(self) -> AsyncIterator[T]:
        yield self.value

    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        return function(self.value)

    async def and_then_await(self, function: AsyncUnary[T, Option[U]]) -> Option[U]:
        return await function(self.value)

    def filter(self, predicate: Predicate[T]) -> Option[T]:
        return self if predicate(self.value) else Null()

    async def filter_await(self, predicate: AsyncPredicate[T]) -> Option[T]:
        return self if await predicate(self.value) else Null()

    def or_else(self, default: Nullary[Option[T]]) -> Some[T]:
        return self

    async def or_else_await(self, default: AsyncNullary[Option[T]]) -> Some[T]:
        return self

    def xor(self, option: Option[T]) -> Option[T]:
        return self if is_null(option) else Null()

    @overload
    def zip(self, option: Null) -> Null:
        ...

    @overload
    def zip(self, option: Some[U]) -> Some[Tuple[T, U]]:
        ...

    @overload
    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        ...

    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        if is_some(option):
            return self.create((self.value, option.value))

        return option  # type: ignore

    @overload
    def zip_with(self, option: Null, function: Binary[T, U, V]) -> Null:
        ...

    @overload
    def zip_with(self, option: Some[U], function: Binary[T, U, V]) -> Some[V]:
        ...

    @overload
    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        ...

    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        if is_some(option):
            return self.create(function(self.value, option.value))

        return Null()

    @overload
    async def zip_with_await(self, option: Null, function: AsyncBinary[T, U, V]) -> Null:
        ...

    @overload
    async def zip_with_await(self, option: Some[U], function: AsyncBinary[T, U, V]) -> Some[V]:
        ...

    @overload
    async def zip_with_await(self, option: Option[U], function: AsyncBinary[T, U, V]) -> Option[V]:
        ...

    async def zip_with_await(self, option: Option[U], function: AsyncBinary[T, U, V]) -> Option[V]:
        if is_some(option):
            return self.create(await function(self.value, option.value))

        return Null()

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


def is_some(option: Option[T]) -> TypeGuard[Some[T]]:
    """This is the same as [`Option.is_some`][wraps.option.OptionProtocol.is_some],
    except it works as a *type guard*.
    """
    return option.is_some()


def is_null(option: Option[T]) -> TypeGuard[Null]:
    """This is the same as [`Option.is_null`][wraps.option.OptionProtocol.is_null],
    except it works as a *type guard*.
    """
    return option.is_null()


def wrap_option(function: Callable[P, T]) -> Callable[P, Option[T]]:
    """Wraps a `function` returning `T` into a function returning
    [`Option[T]`][wraps.option.Option].

    This handles all exceptions via returning [`Null`][wraps.option.Null] on errors,
    wrapping the resulting `value` into [`Some(value)`][wraps.option.Some].

    Example:
        ```python
        @wrap_option
        def parse(string: str) -> int:
            return int(string)

        assert parse("128").is_some()
        assert parse("uwu").is_null()
        ```

    Arguments:
        function: The function to wrap.

    Returns:
        The wrapping function.
    """

    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(function(*args, **kwargs))

        except Exception:
            return Null()

    return wrap


def wrap_option_await(function: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[Option[T]]]:
    """Wraps an asynchronous `function` returning `T` into an asynchronous function returning
    [`Option[T]`][wraps.option.Option].

    This handles all exceptions via returning [`Null`][wraps.option.Null] on errors,
    wrapping the resulting `value` into [`Some(value)`][wraps.option.Some].

    Example:
        ```python
        @wrap_option_await
        async def parse(string: str) -> int:
            return int(string)

        assert (await parse("256")).is_some()
        assert (await parse("uwu")).is_null()
        ```

    Arguments:
        function: The asynchronous function to wrap.

    Returns:
        The asynchronous wrapping function.
    """

    async def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(await function(*args, **kwargs))

        except Exception:
            return Null()

    return wrap


def wrap_optional(optional: Optional[T]) -> Option[T]:
    if optional is None:
        return Null()

    return Some(optional)


# import cycle solution
from iters.async_iters import AsyncIter, async_iter
from iters.iters import Iter, iter

from wraps.result import Error, Ok, Result
