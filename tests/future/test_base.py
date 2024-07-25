import pytest
from funcs.functions import asyncify
from wraps.futures.base import Future


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
async def test_future_map_result() -> None:
    value = 69

    expected = str(value)

    future = Future.from_value(value).map_result(str)

    result = await future

    assert result == expected


async_str = asyncify(str)


@pytest.mark.anyio
async def test_future_map_result_await() -> None:
    value = 7

    expected = str(value)

    future = Future.from_value(value).map_result_await(async_str)

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
async def test_future_flatten_result() -> None:
    value = 13

    nested = Future.from_value(Future.from_value(value))

    future = nested.flatten_result()

    result = await future

    assert result is value
