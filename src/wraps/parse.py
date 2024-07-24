from typing import Generic, Protocol, Self, Type, TypeVar

from named import get_name
from typing_aliases import required

from wraps.primitives.result import Result

__all__ = ("ParseError", "FromString", "ToString", "to_string")

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)

PARSE_FAILED = "parsing `{}` into `{}` failed ({})"
parse_failed = PARSE_FAILED.format


class ParseError(ValueError, Generic[T, E]):
    def __init__(self, string: str, type: Type[T], error: E) -> None:
        self._string = string
        self._type = type
        self._error = error

        super().__init__(parse_failed(string, get_name(type), error))  # type: ignore[arg-type]

    @property
    def string(self) -> str:
        return self._string

    @property
    def type(self) -> Type[T]:
        return self._type

    @property
    def error(self) -> E:
        return self._error


class FromString(Protocol[E]):
    @classmethod
    @required
    def from_string(cls, string: str) -> Result[Self, E]: ...

    @classmethod
    def parse(cls, string: str) -> Self:
        result = cls.from_string(string)

        if result.is_ok():
            return result.unwrap()

        raise ParseError(string, cls, result.unwrap_error())


class ToString(Protocol):
    @required
    def to_string(self) -> str: ...

    def __str__(self) -> str:
        return self.to_string()


def to_string(item: ToString) -> str:
    return item.to_string()
