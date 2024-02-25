from typing import Callable, TypeVar

from typing_extensions import ParamSpec

from wraps.future.base import Future

P = ParamSpec("P")
T = TypeVar("T")

FutureCallable = Callable[P, Future[T]]
