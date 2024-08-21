from __future__ import annotations

from typing import Generic, Protocol, Type, TypeVar, runtime_checkable

from named import get_name
from typing_aliases import required
from typing_extensions import Self

from wraps.result import Result

__all__ = ("FromString", "ParseError")

T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)

PARSE_FAILED = "parsing `{}` into `{}` failed ({})"
parse_failed = PARSE_FAILED.format


class ParseError(ValueError, Generic[T, E]):
    """Represents parse errors."""

    def __init__(self, string: str, type: Type[T], error: E) -> None:
        self._string = string
        self._type = type
        self._error = error

        super().__init__(parse_failed(string, get_name(type), error))  # type: ignore[arg-type]

    @property
    def string(self) -> str:
        """The string that could not be parsed."""
        return self._string

    @property
    def type(self) -> Type[T]:
        """The type parsing into which failed."""
        return self._type

    @property
    def error(self) -> E:
        """The error returned by the
        [`from_string`][wraps.parse.normal.FromString.from_string] function.
        """
        return self._error


@runtime_checkable
class FromString(Protocol[E]):
    """Represents types that can be parsed from strings."""

    @classmethod
    @required
    def from_string(cls, string: str) -> Result[Self, E]:
        """Parses the given string to return some value of type `Self`.

        Arguments:
            string: The string to parse.

        Returns:
            The parse result, [`Ok[Self]`][wraps.result.Ok] if parsing was successful,
                and [`Error[E]`][wraps.result.Error] otherwise.
        """
        ...

    @classmethod
    def parse(cls, string: str) -> Self:
        """Calls [`from_string`][wraps.parse.normal.FromString.from_string] and raises
        [`ParseError[Self, E]`][wraps.parse.normal.ParseError] if parsing fails.

        Arguments:
            string: The string to parse.

        Returns:
            The parsed value.

        Raises:
            ParseError[Self, E]: In case parsing fails.
        """
        result = cls.from_string(string)

        if result.is_ok():
            return result.unwrap()

        raise ParseError(string, cls, result.unwrap_err())
