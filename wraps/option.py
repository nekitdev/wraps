from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Callable,
    Generic,
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
from typing_extensions import Literal, Never, ParamSpec, TypeGuard

from wraps.errors import OptionShortcut, panic
from wraps.typing import AnyException, Binary, Nullary, Predicate, Unary

__all__ = ("Option", "Some", "Null", "is_some", "is_null", "wrap_option", "convert_optional")

P = ParamSpec("P")

T = TypeVar("T", covariant=True)
U = TypeVar("U")
V = TypeVar("V")

E = TypeVar("E")

UNWRAP_ON_NULL = "called `unwrap` on null"


class BaseOption(ABC, Generic[T]):
    def __iter__(self) -> Iterator[T]:
        return self.iter()

    @abstractmethod
    def is_some(self) -> bool:
        ...

    @abstractmethod
    def is_some_and(self, predicate: Predicate[T]) -> bool:
        ...

    @abstractmethod
    def is_null(self) -> bool:
        ...

    @abstractmethod
    def expect(self, message: str) -> T:
        ...

    @abstractmethod
    def unwrap(self) -> T:
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:  # type: ignore
        ...

    @abstractmethod
    def unwrap_or_else(self, default: Nullary[T]) -> T:  # type: ignore
        ...

    @abstractmethod
    def unwrap_or_raise(self, exception: AnyException) -> T:
        ...

    @abstractmethod
    def map(self, function: Unary[T, U]) -> Option[U]:
        ...

    @abstractmethod
    def map_or(self, default: U, function: Unary[T, U]) -> U:
        ...

    @abstractmethod
    def map_or_else(self, default: Nullary[U], function: Unary[T, U]) -> U:
        ...

    @abstractmethod
    def ok_or(self, error: E) -> Result[T, E]:
        ...

    @abstractmethod
    def ok_or_else(self, error: Nullary[E]) -> Result[T, E]:
        ...

    @abstractmethod
    def iter(self) -> Iterator[T]:
        ...

    @abstractmethod
    def and_then(self, function: Unary[T, Option[U]]) -> Option[U]:
        ...

    @abstractmethod
    def filter(self, predicate: Predicate[T]) -> Option[T]:
        ...

    @abstractmethod
    def or_else(self, default: Nullary[Option[T]]) -> Option[T]:
        ...

    @abstractmethod
    def xor(self, option: Option[T]) -> Option[T]:
        ...

    @abstractmethod
    def zip(self, option: Option[U]) -> Option[Tuple[T, U]]:
        ...

    @abstractmethod
    def zip_with(self, option: Option[U], function: Binary[T, U, V]) -> Option[V]:
        ...

    @abstractmethod
    def unzip(self: BaseOption[Tuple[U, V]]) -> Tuple[Option[U], Option[V]]:
        ...

    @abstractmethod
    def transpose(self: BaseOption[BaseResult[T, E]]) -> Result[Option[T], E]:
        ...

    @abstractmethod
    def flatten(self: BaseOption[BaseOption[U]]) -> Option[U]:
        ...

    @abstractmethod
    def contains(self, value: U) -> bool:
        ...

    @property
    @abstractmethod
    def Q(self) -> T:
        ...


@final
@frozen()
class Null(BaseOption[Never]):
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

    def transpose(self: BaseOption[Result[T, E]]) -> Result[Null, E]:
        return Ok(self)  # type: ignore

    def flatten(self: BaseOption[BaseOption[U]]) -> Null:
        return self  # type: ignore

    def contains(self, value: U) -> Literal[False]:
        return False

    @property
    def Q(self) -> Never:
        raise OptionShortcut()


@final
@frozen()
class Some(BaseOption[T]):
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
from wraps.result import BaseResult, Error, Ok, Result, is_ok
