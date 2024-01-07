import pytest
from funcs import asyncify

from wraps.future.base import Future


@pytest.mark.anyio
async def test_future_from_value() -> None:
    value = 13

    future = Future.from_value(value)

    result = await future

    assert result is value


@pytest.mark.anyio
async def test_future_async_iter() -> None:
    value = 42

    future = Future.from_value(value)

    async for result in future:
        assert result is value


@pytest.mark.anyio
async def test_future_base_map() -> None:
    value = 69

    expected = str(value)

    future = Future.from_value(value).base_map(str)

    result = await future

    assert result == expected


async_str = asyncify(str)


@pytest.mark.anyio
async def test_future_base_map_await() -> None:
    value = 7

    expected = str(value)

    future = Future.from_value(value).base_map_await(async_str)

    result = await future

    assert result == expected


def future_str(value: int) -> Future[str]:
    return Future.from_value(str(value))


@pytest.mark.anyio
async def test_future_then() -> None:
    value = 22

    expected = str(value)

    future = Future.from_value(value).then(future_str)

    result = await future

    assert result == expected


@pytest.mark.anyio
async def test_future_base_flatten() -> None:
    value = 13

    nested = Future.from_value(Future.from_value(value))

    future = nested.base_flatten()

    result = await future

    assert result is value
