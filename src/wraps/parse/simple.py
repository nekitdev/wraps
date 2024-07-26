from typing import Generic, Protocol, Type, TypeVar, runtime_checkable

from named import get_name
from typing_aliases import required
from typing_extensions import Self

from wraps.primitives.option import Option

__all__ = ("SimpleFromString", "SimpleParseError")

T = TypeVar("T", covariant=True)

SIMPLE_PARSE_FAILED = "parsing `{}` into `{}` failed"
simple_parse_failed = SIMPLE_PARSE_FAILED.format


class SimpleParseError(ValueError, Generic[T]):
    def __init__(self, string: str, type: Type[T]) -> None:
        self._string = string
        self._type = type

        super().__init__(simple_parse_failed(string, get_name(type)))  # type: ignore[arg-type]

    @property
    def string(self) -> str:
        return self._string

    @property
    def type(self) -> Type[T]:
        return self._type


@runtime_checkable
class SimpleFromString(Protocol):
    @classmethod
    @required
    def from_string(cls, string: str) -> Option[Self]: ...

    @classmethod
    def parse(cls, string: str) -> Self:
        return cls.from_string(string).or_raise(SimpleParseError(string, cls))
