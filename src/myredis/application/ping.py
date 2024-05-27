from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

T = TypeVar("T")


class Ping(Generic[T]):
    def __init__(self, view: Callable[[], T]) -> None:
        self._view = view

    def __call__(self) -> Coroutine[T]:
        yield None
        return self._view()
