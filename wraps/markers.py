from typing_extensions import Never

from wraps.errors import panic

__all__ = ("unreachable",)

UNREACHABLE = "code marked with `unreachable` was reached"


def unreachable() -> Never:
    """Marks points in code as unreachable.

    Panics if called.

    Raises:
        Panic: Always raised when calling.
    """
    panic(UNREACHABLE)
