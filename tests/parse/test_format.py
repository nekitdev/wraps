from __future__ import annotations

from attrs import frozen
from hypothesis import given
from hypothesis.strategies import integers
from wraps.parse.format import ToString, to_short_string, to_string

from tests.parse.base import Integer


@frozen()
class FormatInteger(ToString, Integer):
    def to_string(self) -> str:
        return str(self.value)


def test_to_string() -> None:
    value = 34
    string = "34"

    integer = FormatInteger(value)

    assert integer.to_string() == string
    assert integer.to_short_string() == string
    assert str(integer) == string


@given(integers(min_value=0))
def test_to_string_functions(value: int) -> None:
    integer = FormatInteger(value)

    assert to_string(integer) == integer.to_string()
    assert to_short_string(integer) == integer.to_short_string()
