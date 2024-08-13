from __future__ import annotations

from pytest import fail
from wraps.panics import PANIC, Panic, panic

PANIC_NEVER_RETURNS = "`panic` never returns"


def test_panic() -> None:
    try:
        panic()

    except Panic as error:
        assert error.message is None

        assert str(error) == PANIC

    else:
        fail(PANIC_NEVER_RETURNS)


MESSAGE = "panic..."


def test_panic_message() -> None:
    message = MESSAGE

    try:
        panic(message)

    except Panic as error:
        assert error.message == message

        assert str(error) == message
