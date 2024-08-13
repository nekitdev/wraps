from __future__ import annotations

from typing import Protocol, runtime_checkable

from typing_aliases import required

__all__ = ("ToString", "to_string", "to_short_string")


@runtime_checkable
class ToString(Protocol):
    """Represents types that can be converted to strings."""

    @required
    def to_string(self) -> str:
        """Converts `self` to its string representation.

        Returns:
            The string representation of `self`.
        """
        ...

    def to_short_string(self) -> str:
        """Converts `self` to its (short) string representation.

        The default implementation simply calls [`to_string`][wraps.parse.format.ToString.to_string].

        Returns:
            The (short) string representation of `self`.
        """
        return self.to_string()

    def __str__(self) -> str:
        """Calls [`to_string`][wraps.parse.format.ToString.to_string] and returns the result.

        Returns:
            The string representation of `self`.
        """
        return self.to_string()


def to_string(value: ToString) -> str:
    """Calls [`to_string`][wraps.parse.format.ToString.to_string] method on the given value
    and returns the result.

    Arguments:
        value: The value to convert to string.

    Returns:
        The string representation of `value`.
    """
    return value.to_string()


def to_short_string(value: ToString) -> str:
    """Calls [`to_short_string`][wraps.parse.format.ToString.to_short_string] method
    on the given value and returns the result.

    Arguments:
        value: The value to convert to string.

    Returns:
        The (short) string representation of `value`.
    """
    return value.to_short_string()
