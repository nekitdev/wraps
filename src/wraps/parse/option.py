from typing import Generic, Protocol, Type, TypeVar, runtime_checkable

from named import get_name
from typing_aliases import required
from typing_extensions import Self

from wraps.primitives.option import Option

__all__ = ("OptionParseError", "OptionFromString")

T = TypeVar("T", covariant=True)

OPTION_PARSE_FAILED = "parsing `{}` into `{}` failed"
option_parse_failed = OPTION_PARSE_FAILED.format


class OptionParseError(ValueError, Generic[T]):
    def __init__(self, string: str, type: Type[T]) -> None:
        self._string = string
        self._type = type

        super().__init__(option_parse_failed(string, get_name(type)))  # type: ignore[arg-type]

    @property
    def string(self) -> str:
        return self._string

    @property
    def type(self) -> Type[T]:
        return self._type


@runtime_checkable
class OptionFromString(Protocol):
    @classmethod
    @required
    def from_string(cls, string: str) -> Option[Self]: ...

    @classmethod
    def parse(cls, string: str) -> Self:
        return cls.from_string(string).or_raise(OptionParseError(string, cls))
