"""Panics represented as errors."""

from typing_aliases import AnyError
from typing_extensions import Never


class Panic(AnyError):
    """Represents panics as errors.

    Panics should not be explicitly handled in general, therefore [`Panic`][wraps.panics.Panic]
    is derived from [`AnyError`][typing_aliases.typing.AnyError].
    """


def panic(message: str) -> Never:
    """Panics with the given `message`.

    Arguments:
        message: The message to panic with.

    Raises:
        Panic: Always raised.
    """
    raise Panic(message)
