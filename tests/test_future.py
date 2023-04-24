import pytest

from wraps.future import Future


@pytest.mark.anyio
async def test_future_from_value() -> None:
    value = 42

    future = Future.from_value(value)

    result = await future

    assert result is value
