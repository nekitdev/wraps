from __future__ import annotations

from attrs import frozen
from pytest import fail
from typing_extensions import Self
from wraps.parse.normal import FromString, ParseError
from wraps.result import Err, Ok, Result

from tests.parse.base import Integer, is_digits

NON_DIGIT = "non-digit character found"


@frozen()
class NormalInteger(FromString[str], Integer):
    @classmethod
    def from_string(cls, string: str) -> Result[Self, str]:
        return Ok(cls(int(string))) if is_digits(string) else Err(NON_DIGIT)


def test_from_string_some() -> None:
    string = "34"
    value = 34

    result = NormalInteger.from_string(string)
    integer = NormalInteger(value)

    assert result.is_ok() and result.unwrap() == integer


def test_from_string_null() -> None:
    string = "foo"

    result = NormalInteger.from_string(string)

    assert result.is_err() and result.unwrap_err() == NON_DIGIT


def test_parse() -> None:
    string = "69"
    value = 69

    integer = NormalInteger.parse(string)

    assert integer.value == value


EXPECTED_ERROR = "expected parse error to be raised"


def test_parse_error() -> None:
    string = "bar"

    try:
        NormalInteger.parse(string)

    except ParseError as error:
        assert error.string == string
        assert error.type is NormalInteger
        assert error.error == NON_DIGIT

    else:
        fail(EXPECTED_ERROR)
