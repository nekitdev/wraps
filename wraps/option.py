"""Optional values.

[`Option[T]`][wraps.option.Option] represents an optional value:
every [`Option[T]`][wraps.option.Option] is either [`Some[T]`][wraps.option.Some] and
contains a value (of type `T`), or [`Null`][wraps.option.Null], and does not.

[`Option[T]`][wraps.option.Option] types can be very common in python code,
as they have a number of uses:

- Initial values;
- Return values for functions not defined over their entire input range (partial functions);
- Return value for otherwise reporting simple errors, where [`Null`][wraps.option.Null]
    is returned on error;
- Optional function arguments.

[`Option[T]`][wraps.option.Option] is commonly paired with pattern matching to query
the presence of [`Some[T]`][wraps.option.Some] value (`T`) and take action,
always accounting for the [`Null`][wraps.option.Null] case:

```python
def divide(numerator: float, denominator: float) -> Option[float]:
    if not denominator:
        return Null()

    return Some(numerator / denominator)
```

```python
option = divide(1.0, 2.0)

match option:
    case Some(result):
        print(result)

    case Null():
        print("can not divide by 0")
```
"""

from __future__ import annotations

from abc import abstractmethod
from typing import (
    Callable,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
    overload,
)

from attrs import frozen
from typing_extensions import Literal, Never, ParamSpec, Protocol, TypeGuard

from wraps.errors import OptionShortcut, panic
from wraps.typing import AnyException, Binary, Nullary, Predicate, Unary

__all__ = ("Option", "Some", "Null", "is_some", "is_null", "wrap_option", "convert_optional")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E")

UNWRAP_ON_NULL = "called `unwrap` on null"


class OptionProtocol(Protocol[T]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter()

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def is_null(self) -> bool:
        """Checks if the option is [`Null`][wraps.option.Null].

        Returns:
            Whether the option is [`Null`][wraps.option.Null].
        """
        ...

    @abstractmethod
    def expect(self, message: str) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value.

        Arguments:
            message: The message used in panicking.

        Raises:
            Panic: Panics with `message` if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value.

        Because this function may panic, its use is generally discouraged.

        Instead, prefer to use pattern matching and handle the [`Null`][wraps.option.Null]
        case explicitly, or call [`unwrap_or`][wraps.option.OptionProtocol.unwrap_or]
        or [`unwrap_or_else`][wraps.option.OptionProtocol.unwrap_or_else].

        Raises:
            Panic: Panics if the option is [`Null`][wraps.option.Null].

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:  # type: ignore
        """Returns the contained [`Some[T]`][wraps.option.Some] value or a provided default.

        Arguments:
            default: The default value to use.

        Returns:
            The contained value or `default` one.
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, default: Nullary[T]) -> T:  # type: ignore
        """Returns the contained [`Some[T]`][wraps.option.Some] value or
        computes it from the function.

        Arguments:
            default: The default function to use.

        Returns:
            The contained value or `default()` result.
        """
        ...

    @abstractmethod
    def unwrap_or_raise(self, exception: AnyException) -> T:
        """Returns the contained [`Some[T]`][wraps.option.Some] value or
        raises an exception.

        Arguments:
            exception: The exception to raise.

        Returns:
            The contained value.
        """
        ...

    @abstractmethod
    def map(self, function: Unary[T, U]) -> Option[U]:
        """Maps an [`Option[T]`][wraps.option.Option] to [`Option[U]`][wraps.option.Option]
        by applying `function` to the contained value.

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

    @abstractmethod
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        """Returns the default value (if none), or applies `function`
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

    @abstractmethod
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        """Computes the default value (if none), or applies `function`
        to the contained value (if any).

        Example:
            ```python
            default = lambda: 42

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

    @abstractmethod
    def ok_or(self, error: E) -> Result[T, E]:
        """Transforms the [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Error(error)`][wraps.result.Error].

        Arguments:
            error: The error to use.

        Returns:
            The transformed result.
        """
        ...

    @abstractmethod
    def ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        """Transforms the [`Option[T]`][wraps.option.Option]
        into a [`Result[T, E]`][wraps.result.Result], mapping [`Some(value)`][wraps.option.Some]
        to [`Ok(value)`][wraps.result.Ok] and [`Null`][wraps.option.Null]
        to [`Error(error())`][wraps.result.Error].

        Arguments:
            error: The error function to use.

        Returns:
            The transformed result.
        """
        ...

    @abstractmethod
    def iter(self) -> Iterator[T]:
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

    @abstractmethod
    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls `function` with the wrapped value and returns the result.

        This function is also known as *bind* in functional programming.

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

    @abstractmethod
    def filter(self, predicate: Predicate[T]) -> Option[T]:
        """Returns [`Null`][wraps.option.Null] if the option is [`Null`][wraps.option.Null],
        otherwise calls `predicate` with the wrapped value and returns:

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

    @abstractmethod
    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        """Returns the option if it contains a value, otherwise calls
        `default` and returns the result.

        Example:
            ```python
            # TODO
            ```

        Arguments:
            default: The default function to use.

        Returns:
            The resulting option.
        """
        ...

    @abstractmethod
    def xor(self, option: Option[T]) -> Option[T]:
        """Returns [`Some[T]`][wraps.option.Some] if exactly one of `self` and `option`
        is [`Some[T]`][wraps.option.Option], otherwise returns [`Null`][wraps.option.Null].

        Arguments:
            option: The option to *xor* `self` with.

        Returns:
            The resulting option.
        """
        ...

    @abstractmethod
    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        """Zips `self` with an `option`.

        If `self` is [`Some(s)`][wraps.option.Some] and `option` is [`Some(o)`][wraps.option.Some],
        this method returns [`Some(s, o)`][wraps.option.Some]. Otherwise,
        [`Null`][wraps.option.Null] is returned.

        Arguments:
            option: The option to *zip* `self` with.

        Returns:
            The resulting option.
        """
        ...

    @abstractmethod
    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        """Zips `self` with an `option` using `function`.

        If `self` is [`Some(s)`][wraps.option.Some] and `option` is [`Some(o)`][wraps.option.Some],
        this method returns [`Some(function(s, o))`][wraps.option.Some]. Otherwise,
        [`Null`][wraps.option.Null] is returned.

        Arguments:
            option: The option to *zip* `self` with.
            function: The function to use for zipping.

        Returns:
            The resulting option.
        """
        ...

    @abstractmethod
    def unzip(self: OptionProtocol[Tuple[U, V]]) -> Tuple[Option[U], Option[V]]:
        """Unzips an option into two options.

        If `self` is [`Some((u, v))`][wraps.option.Some], this method returns
        ([`Some(u)`][wraps.option.Some], [`Some(v)`][wraps.option.Some]) tuple.
        Otherwise, ([`Null`][wraps.option.Null], [`Null`][wraps.option.Null]) is returned.

        Returns:
            The resulting tuple of two options.
        """
        ...

    @abstractmethod
    def transpose(self: OptionProtocol[ResultProtocol[T, E]]) -> Result[Option[T], E]:
        """Transposes an option of a result into result of an option.
        This function maps [`Option[Result[T, E]]`][wraps.option.Option] into
        [`Result[Option[T], E]]`][wraps.result.Result] in the following way:

        - [`Null()`][wraps.option.Null] is mapped to [`Ok(Null())`][wraps.result.Ok];
        - [`Some(Ok(value))`][wraps.option.Some] is mapped to [`Ok(Some(value))`][wraps.result.Ok];
        - [`Some(Error(error))`][wraps.option.Some] is mapped to
          [`Error(Some(error))`][wraps.result.Error].

        Returns:
            The transposed result.
        """
        ...

    @abstractmethod
    def flatten(self: OptionProtocol[OptionProtocol[U]]) -> Option[U]:
        """Flattens an [`Option[Option[T]]`][wraps.option.Option]
        to [`Option[T]`][wraps.option.Option].

        Returns:
            The flattened option.
        """
        ...

    @abstractmethod
    def contains(self, value: U) -> bool:
        """Checks if the contained value (if any) is equal to `value`.

        Arguments:
            value: The value to check against.

        Returns:
            Whether the contained value is equal to `value`.
        """
        ...

    @property
    @abstractmethod
    def Q(self) -> T:
        """Functionally similar to `?` operator in Rust."""
        ...


@final
@frozen()
class Null(OptionProtocol[Never]):
    """[`Null`][wraps.option.Null] variant of [`Option[T]`][wraps.option.Option]."""

    def __bool__(self) -> Literal[False]:
        return False

    def is_some(self) -> Literal[False]:
        return False

    def is_some_and(self, predicate: Predicate[T]) -> Literal[False]:
        return False

    def is_null(self) -> Literal[True]:
        return True

    def expect(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> Never:
        panic(UNWRAP_ON_NULL)

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, default: Nullary[U]) -> U:
        return default()

    def unwrap_or_raise(self, exception: AnyException) -> Never:
        raise exception

    def map(self, function: Unary[T, U]) -> Null:
        return self

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return default

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return default()

    def ok_or(self, error: E) -> Error[E]:
        return Error(error)

    def ok_or_else(self, error: Nullary[E]) -> Error[E]:
        return Error(error())

    def iter(self) -> Iterator[Never]:
        return
        yield  # type: ignore

    def and_then(self, function: Unary[T, Option[U]]) -> Null:
        return self

    def filter(self, predicate: Predicate[T]) -> Null:
        return self

    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        return default()

    def xor(self, option: Option[T]) -> Option[T]:
        return option

    def zip(self, option: Option[U]) -> Null:
        return self

    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Null:
        return self

    def unzip(self) -> Tuple[Null, Null]:
        return self, self

    def transpose(self: OptionProtocol[Result[T, E]]) -> Result[Null, E]:
        return Ok(self)  # type: ignore

    def flatten(self: OptionProtocol[OptionProtocol[U]]) -> Null:
        return self  # type: ignore

    def contains(self, value: U) -> Literal[False]:
        return False

    @property
    def Q(self) -> Never:
        raise OptionShortcut()


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

    def is_null(self) -> Literal[False]:
        return False

    def expect(self, message: str) -> T:
        return self.value

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:  # type: ignore
        return self.value

    def unwrap_or_else(self, default: Nullary[T]) -> T:
        return self.value

    def unwrap_or_raise(self, exception: AnyException) -> T:
        return self.value

    def map(self, function: Unary[T, U]) -> Some[U]:
        return self.create(function(self.value))

    def map_or(self, default: U, function: Unary[T, U]) -> U:
        return function(self.value)

    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        return function(self.value)

    def ok_or(self, error: E) -> Ok[T]:
        return Ok(self.value)

    def ok_or_else(self, error: Nullary[E]) -> Ok[T]:
        return Ok(self.value)

    def iter(self) -> Iterator[T]:
        yield self.value

    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        return function(self.value)

    def filter(self, predicate: Predicate[T], null_type: Type[Null] = Null) -> Option[T]:
        return self if predicate(self.value) else null_type()

    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        return self

    def xor(self, option: Option[T], null_type: Type[Null] = Null) -> Option[T]:
        return self if is_null(option) else null_type()

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

        return option.create()  # type: ignore

    def unzip(self: Some[Tuple[U, V]]) -> Tuple[Some[U], Some[V]]:
        u, v = self.value

        return self.create(u), self.create(v)

    def flatten(self: Some[Option[U]]) -> Option[U]:
        return self.value

    @overload
    def transpose(self: Some[Ok[T]]) -> Ok[Some[T]]:
        ...

    @overload
    def transpose(self: Some[Error[E]]) -> Error[E]:
        ...

    @overload
    def transpose(self: Some[Result[T, E]]) -> Result[Option[T], E]:
        ...

    def transpose(self: Some[Result[T, E]]) -> Result[Option[T], E]:
        result = self.value

        if is_ok(result):
            return result.create(self.create(result.value))  # type: ignore

        return result  # type: ignore

    def contains(self, value: U) -> bool:
        return self.value == value

    @property
    def Q(self) -> T:
        return self.value


Option = Union[Some[T], Null]
"""Optional value, expressed as the union of [`Some[T]`][wraps.option.Some]
and [`Null`][wraps.option.Null].
"""


def is_some(option: Option[T]) -> TypeGuard[Some[T]]:
    return option.is_some()


def is_null(option: Option[T]) -> TypeGuard[Null]:
    return option.is_null()


def wrap_option(function: Callable[P, T]) -> Callable[P, Option[T]]:
    def wrap(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            return Some(function(*args, **kwargs))

        except Exception:
            return Null()

    return wrap


def convert_optional(optional: Optional[T]) -> Option[T]:
    if optional is None:
        return Null()

    return Some(optional)


# import cycle solution
from wraps.result import Error, Ok, Result, ResultProtocol, is_ok
