from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

T_co = TypeVar("T_co")


class Ping(Generic[T_co]):
    def __init__(self, view: Callable[[], T_co]) -> None:
        self._view = view

    def __call__(self) -> Coroutine[T_co]:
        yield None
        return self._view()
