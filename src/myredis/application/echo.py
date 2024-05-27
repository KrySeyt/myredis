from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

T = TypeVar("T")


class Echo(Generic[T]):
    def __init__(self, view: Callable[[str], T]) -> None:
        self._view = view

    def __call__(self, value: str) -> Coroutine[T]:
        yield None
        return self._view(value)
