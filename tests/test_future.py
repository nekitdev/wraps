from typing import TypeVar

import pytest

from wraps.future import Future, wrap_future

T = TypeVar("T")


async def async_identity(item: T) -> T:
    return item


@pytest.mark.anyio
async def test_future_identity() -> None:
    value = 34

    assert await Future(async_identity(value)) is value


@pytest.mark.anyio
async def test_future_map() -> None:
    value = 13
    result = 13.0

    assert await Future(async_identity(value)).map(float) == result


@pytest.mark.anyio
async def test_future_from_value() -> None:
    value = 42

    assert await Future.from_value(value) is value
