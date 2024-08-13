from __future__ import annotations

from entrypoint import entrypoint
from named import get_name
from wraps.either import EitherProtocol
from wraps.futures.either import FutureEither
from wraps.futures.option import FutureOption
from wraps.futures.result import FutureResult
from wraps.option import OptionProtocol
from wraps.result import ResultProtocol

PROTOCOL_TO_FUTURE = {
    EitherProtocol: FutureEither,
    OptionProtocol: FutureOption,
    ResultProtocol: FutureResult,
}

UNDER = "_"
starts_with = str.startswith

ITER = "iter"


def is_skipped(name: str) -> bool:
    return starts_with(name, UNDER) or ITER in name


CHECKING_INTEGRITY = "checking integrity of `{}` with `{}`..."
checking_integrity = CHECKING_INTEGRITY.format

MISSING = "`{}` is missing"
missing = MISSING.format


@entrypoint(__name__)
def main() -> None:
    for protocol, future in PROTOCOL_TO_FUTURE.items():
        print(checking_integrity(get_name(protocol), get_name(future)))

        names = vars(future)

        for name in vars(protocol):
            if is_skipped(name):
                continue

            if name not in names:
                print(missing(name))
