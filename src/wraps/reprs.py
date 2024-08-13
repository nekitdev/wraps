from __future__ import annotations

from typing import Any

from named import get_type_name

__all__ = ("empty_repr", "wrap_repr")

EMPTY_REPRESENTATION = "{name}()"
empty_representation = EMPTY_REPRESENTATION.format

WRAP_REPRESENTATION = "{name}({value!r})"
wrap_representation = WRAP_REPRESENTATION.format


def empty_repr(self: Any) -> str:
    return empty_representation(name=get_type_name(self))


def wrap_repr(self: Any, value: Any) -> str:
    return wrap_representation(name=get_type_name(self), value=value)
