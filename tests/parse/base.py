from __future__ import annotations

from attrs import field, frozen
from attrs.validators import ge

__all__ = ("Integer", "is_digits")

is_digits = str.isdigit


@frozen()
class Integer:
    value: int = field(validator=ge(0))
