from __future__ import annotations

from attrs import frozen
from pytest import fail
from typing_extensions import Self
from wraps.option import NULL, Option, Some
from wraps.parse.simple import SimpleFromString, SimpleParseError

from tests.parse.base import Integer, is_digits


@frozen()
class SimpleInteger(SimpleFromString, Integer):
    @classmethod
    def from_string(cls, string: str) -> Option[Self]:
        return Some(cls(int(string))) if is_digits(string) else NULL


def test_from_string_some() -> None:
    string = "13"
    value = 13

    option = SimpleInteger.from_string(string)
    integer = SimpleInteger(value)

    assert option.is_some() and option.unwrap() == integer


def test_from_string_null() -> None:
    string = "foo"

    option = SimpleInteger.from_string(string)

    assert option.is_null()


def test_parse() -> None:
    string = "13"
    value = 13

    integer = SimpleInteger.parse(string)

    assert integer.value == value


EXPECTED_ERROR = "expected parse error to be raised"


def test_parse_error() -> None:
    string = "bar"

    try:
        SimpleInteger.parse(string)

    except SimpleParseError as error:
        assert error.string == string
        assert error.type is SimpleInteger

    else:
        fail(EXPECTED_ERROR)
