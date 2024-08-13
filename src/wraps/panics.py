"""Panics represented as errors."""

from __future__ import annotations

from typing import Optional

from typing_aliases import AnyError
from typing_extensions import Never

__all__ = ("PANIC", "Panic", "panic")

PANIC = "panic!"


class Panic(AnyError):
    """Represents panics as errors.

    Panics should not be explicitly handled in general, therefore [`Panic`][wraps.panics.Panic]
    is derived from [`AnyError`][typing_aliases.AnyError].
    """

    def __init__(self, message: Optional[str] = None) -> None:
        self._message = message

        if message is None:
            message = PANIC

        super().__init__(message)

    @property
    def message(self) -> Optional[str]:
        return self._message


def panic(message: Optional[str] = None) -> Never:
    """Panics with the optional message.

    Arguments:
        message: The message to panic with.

    Raises:
        Panic: Always raised.
    """
    raise Panic(message)
