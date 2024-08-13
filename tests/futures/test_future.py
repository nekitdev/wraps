from __future__ import annotations

import pytest
from wraps.futures.future import future_value, wrap_future


async def square(value: int) -> int:
    return value * value


future_square = wrap_future(square)


@pytest.mark.anyio
async def test_future_value() -> None:
    value = 42

    future = future_value(value)

    assert await future == value


@pytest.mark.anyio
async def test_future_map() -> None:
    value = 13

    result = "169"

    future = future_value(value).future_map_await(future_square).future_map(str)

    assert await future == result


@pytest.mark.anyio
async def test_future_then() -> None:
    value = 13

    result = 169

    future = future_value(value).then(future_square)

    assert await future == result


@pytest.mark.anyio
async def test_future_flatten() -> None:
    value = 42

    nested = future_value(future_value(value))

    future = nested.future_flatten()

    assert await future == value


@pytest.mark.anyio
async def test_future_async_iter() -> None:
    value = 13

    count = 0

    async for result in future_value(value):
        assert result == value

        count += 1

    assert count == 1  # result only yielded once
