from __future__ import annotations

from typing import Generic, Protocol, Type, TypeVar, runtime_checkable

from named import get_name
from typing_aliases import required
from typing_extensions import Self

from wraps.option import Option

__all__ = ("SimpleFromString", "SimpleParseError")

T = TypeVar("T", covariant=True)

SIMPLE_PARSE_FAILED = "parsing `{}` into `{}` failed"
simple_parse_failed = SIMPLE_PARSE_FAILED.format


class SimpleParseError(ValueError, Generic[T]):
    """Represents simple parse errors."""

    def __init__(self, string: str, type: Type[T]) -> None:
        self._string = string
        self._type = type

        super().__init__(simple_parse_failed(string, get_name(type)))  # type: ignore[arg-type]

    @property
    def string(self) -> str:
        """The string that could not be parsed."""
        return self._string

    @property
    def type(self) -> Type[T]:
        """The type parsing into which failed."""
        return self._type


@runtime_checkable
class SimpleFromString(Protocol):
    """Represents types that can be parsed from strings."""

    @classmethod
    @required
    def from_string(cls, string: str) -> Option[Self]:
        """Parses the given string to return some value of type `Self`.

        Arguments:
            string: The string to parse.

        Returns:
            The parse result, [`Some[Self]`][wraps.option.Some] if parsing was successful,
                and [`Null`][wraps.option.Null] otherwise.
        """
        ...

    @classmethod
    def parse(cls, string: str) -> Self:
        """Calls [`from_string`][wraps.parse.simple.SimpleFromString.from_string] and raises
        [`SimpleParseError[Self]`][wraps.parse.simple.SimpleParseError] if parsing fails.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed value.

        Raises:
            SimpleParseError[Self]: In case parsing fails.
        """
        return cls.from_string(string).or_raise(SimpleParseError(string, cls))
