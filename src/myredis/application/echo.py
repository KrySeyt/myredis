from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

T_co = TypeVar("T_co")


class Echo(Generic[T_co]):
    def __init__(self, view: Callable[[str], T_co]) -> None:
        self._view = view

    def __call__(self, value: str) -> Coroutine[T_co]:
        yield None
        return self._view(value)
