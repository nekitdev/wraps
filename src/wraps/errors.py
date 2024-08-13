from __future__ import annotations

from typing import Generic, Type, TypeVar, final

from attrs import Attribute, field, frozen
from typing_aliases import AnyError, DynamicTuple, EmptyTuple
from typing_extensions import Self, TypeIs

from wraps.panics import panic

__all__ = ("RawErrorTypes", "ErrorTypes")

T = TypeVar("T")


def is_empty_tuple(dynamic_tuple: DynamicTuple[T]) -> TypeIs[EmptyTuple]:
    return not dynamic_tuple


E = TypeVar("E", bound=AnyError)

RawErrorTypes = DynamicTuple[Type[E]]
"""Represents error types. `E` is bound to [`AnyError`][typing_aliases.AnyError]."""

EXPECTED_ERROR_TYPES = "`ErrorTypes[E]` expected non-empty `RawErrorTypes[E]`, got `{}`"
expected_error_types = EXPECTED_ERROR_TYPES.format


@final
@frozen()
class ErrorTypes(Generic[E]):
    """Represents non-empty error types. `E` is bound to [`AnyError`][typing_aliases.AnyError]."""

    raw: RawErrorTypes[E] = field()
    """Raw error types."""

    @raw.validator
    def check_raw(self, attribute: Attribute[RawErrorTypes[E]], value: RawErrorTypes[E]) -> None:
        if is_empty_tuple(value):
            panic(expected_error_types(value))

    @classmethod
    def from_head_and_tail(cls, head: Type[E], *tail: Type[E]) -> Self:
        raw = (head, *tail)

        return cls(raw)

    def extract(self) -> RawErrorTypes[E]:
        return self.raw
