from wraps.futures.typing.base import (
    FutureBinary,
    FutureCallable,
    FutureNullary,
    FutureQuaternary,
    FutureTernary,
    FutureUnary,
)
from wraps.futures.typing.derived import (
    FutureEitherCallable,
    FutureOptionCallable,
    FutureResultCallable,
)

__all__ = (
    # base
    "FutureCallable",
    "FutureNullary",
    "FutureUnary",
    "FutureBinary",
    "FutureTernary",
    "FutureQuaternary",
    # derived
    "FutureOptionCallable",
    "FutureResultCallable",
    "FutureEitherCallable",
)
