import pytest

from wraps.future import Future, wrap_future


@pytest.mark.anyio
async def test_future_from_value() -> None:
    value = 42

    future = Future.from_value(value)

    assert await future is value


@pytest.mark.anyio
async def test_future_map() -> None:
    value = 13
    result = 13.0

    future = Future.from_value(value)

    assert await future.map_future(float) == result
