from __future__ import annotations

from abc import abstractmethod
from functools import wraps
from typing import Callable, Generic, Iterator, Type, TypeVar, Union, final, overload

from attrs import frozen
from typing_extensions import Literal, Never, ParamSpec, Protocol, TypeGuard

from wraps.errors import ResultShortcut, panic
from wraps.option import OptionProtocol, Null, Option, Some, is_some
from wraps.typing import AnyException, Nullary, Predicate, Unary

__all__ = ("Result", "Ok", "Error", "is_ok", "is_error", "WrapResult", "wrap_result")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
E = TypeVar("E", covariant=True)
F = TypeVar("F")

UNWRAP_ON_ERROR = "called `unwrap` on error"
UNWRAP_ERROR_ON_OK = "called `unwrap_error` on ok"


class ResultProtocol(Protocol[T, E]):  # type: ignore[misc]
    def __iter__(self) -> Iterator[T]:
        return self.iter()

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
        ...

    @abstractmethod
    def is_error(self) -> bool:
        """Checks if the result is [`Error[E]`][wraps.result.Error].

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
    def is_error_and(self, predicate: Predicate[E]) -> bool:
        ...

    @abstractmethod
    def expect(self, message: str) -> T:
        ...

    @abstractmethod
    def expect_error(self, message: str) -> E:
        ...

    @abstractmethod
    def unwrap(self) -> T:
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:  # type: ignore
        ...

    @abstractmethod
    def unwrap_or_else(self, default: Nullary[T]) -> T:
        ...

    @abstractmethod
    def unwrap_or_raise(self, exception: AnyException) -> T:
        ...

    @abstractmethod
    def unwrap_error(self) -> E:
        ...

    @abstractmethod
    def unwrap_error_or(self, default: E) -> E:  # type: ignore
        ...

    @abstractmethod
    def unwrap_error_or_else(self, default: Nullary[E]) -> E:
        ...

    @abstractmethod
    def unwrap_error_or_raise(self, exception: AnyException) -> E:
        ...

    @abstractmethod
    def ok(self) -> Option[T]:
        ...

    @abstractmethod
    def error(self) -> Option[E]:
        ...

    @abstractmethod
    def map(self, function: Unary[T, U]) -> Result[U, E]:
        ...

    @abstractmethod
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        ...

    @abstractmethod
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        ...

    @abstractmethod
    def map_error(self, function: Unary[E, F]) -> Result[T, F]:
        ...

    @abstractmethod
    def map_error_or(self, default: F, function: Unary[E, F]) -> F:
        ...

    @abstractmethod
    def map_error_or_else(self, default: Nullary[F], function: Unary[E, F]) -> F:
        ...

    @abstractmethod
    def iter(self) -> Iterator[T]:
        ...

    @abstractmethod
    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        ...

    @abstractmethod
    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        ...

    @abstractmethod
    def transpose(self: ResultProtocol[OptionProtocol[T], E]) -> Option[Result[T, E]]:
        ...

    @abstractmethod
    def contains(self, value: U) -> bool:
        ...

    @abstractmethod
    def contains_error(self, error: F) -> bool:
        ...

    @abstractmethod
    def swap(self) -> Result[E, T]:
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

    def is_error(self) -> Literal[False]:
        return False

    def is_error_and(self, predicate: Predicate[E]) -> Literal[False]:
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

    def unwrap_or_raise(self, exception: AnyException) -> T:
        return self.value

    def unwrap_error(self) -> Never:
        panic(UNWRAP_ERROR_ON_OK)

    def unwrap_error_or(self, default: F) -> F:
        return default

    def unwrap_error_or_else(self, default: Nullary[F]) -> F:
        return default()

    def unwrap_error_or_raise(self, exception: AnyException) -> Never:
        raise exception

    def ok(self) -> Some[T]:
        return Some(self.value)

    def error(self) -> Null:
        return Null()

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

    def iter(self) -> Iterator[T]:
        yield self.value

    def and_then(self, function: Unary[T, Result[U, E]]) -> Result[U, E]:
        return function(self.value)

    def or_else(self, function: Unary[E, Result[T, F]]) -> Ok[T]:
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

    def swap(self) -> Error[T]:
        return Error(self.value)

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

    def is_error(self) -> Literal[True]:
        return True

    def is_error_and(self, predicate: Predicate[E]) -> bool:
        return predicate(self.value)

    def ok(self) -> Null:
        return Null()

    def error(self) -> Some[E]:
        return Some(self.value)

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

    def iter(self) -> Iterator[Never]:
        return
        yield  # type: ignore

    def expect(self, message: str) -> Never:
        panic(message)

    def unwrap(self) -> Never:
        panic(UNWRAP_ON_ERROR)

    def expect_error(self, message: str) -> E:
        return self.value

    def unwrap_error(self) -> E:
        return self.value

    def and_then(self, function: Unary[T, Result[U, E]]) -> Error[E]:
        return self

    def or_else(self, function: Unary[E, Result[T, F]]) -> Result[T, F]:
        return function(self.value)

    def unwrap_or(self, default: U) -> U:
        return default

    def unwrap_or_else(self, default: Nullary[U]) -> U:
        return default()

    def unwrap_or_raise(self, exception: AnyException) -> Never:
        raise exception

    def unwrap_error_or(self, default: F) -> E:
        return self.value

    def unwrap_error_or_else(self, default: Nullary[F]) -> E:
        return self.value

    def unwrap_error_or_raise(self, exception: AnyException) -> E:
        return self.value

    def transpose(self: Error[E], some_type: Type[Some[Error[E]]] = Some) -> Some[Error[E]]:
        return some_type(self)

    def contains(self, value: U) -> Literal[False]:
        return False

    def contains_error(self, error: F) -> bool:
        return self.value == error

    def swap(self) -> Ok[E]:
        return Ok(self.value)

    @property
    def Q(self) -> Never:
        raise ResultShortcut(self.value)


Result = Union[Ok[T], Error[E]]
"""Result value, expressed as the union of [`Ok[T]`][wraps.result.Ok]
and [`Error[E]`][wraps.result.Error].
"""


def is_ok(result: Result[T, E]) -> TypeGuard[Ok[T]]:
    return result.is_ok()


def is_error(result: Result[T, E]) -> TypeGuard[Error[E]]:
    return result.is_error()


AE = TypeVar("AE", bound=AnyException)
AF = TypeVar("AF", bound=AnyException)


class WrapResult(Generic[AE]):
    def __init__(self, error_type: Type[AE]) -> None:
        self._error_type = error_type

    @classmethod
    def create(cls, error_type: Type[AF]) -> WrapResult[AF]:
        return cls(error_type)  # type: ignore

    @property
    def error_type(self) -> Type[AE]:
        return self._error_type

    def __call__(self, function: Callable[P, T]) -> Callable[P, Result[T, AE]]:
        @wraps(function)
        def wrap(*args: P.args, **kwargs: P.kwargs) -> Result[T, AE]:
            try:
                return Ok(function(*args, **kwargs))

            except self.error_type as error:
                return Error(error)

        return wrap

    def __getitem__(self, error_type: Type[AF]) -> WrapResult[AF]:
        return self.create(error_type)


wrap_result = WrapResult(Exception)
