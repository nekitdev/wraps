from typing_extensions import Never

from wraps.errors import panic

__all__ = ("unreachable",)

UNREACHABLE = "code marked with `unreachable` was reached"


def unreachable() -> Never:
    panic(UNREACHABLE)
