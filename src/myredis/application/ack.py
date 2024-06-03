from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

ViewT = TypeVar("ViewT")


class Ack(Generic[ViewT]):
    def __init__(self, view: Callable[[], ViewT]) -> None:
        self._view = view

    def __call__(self) -> Coroutine[ViewT]:
        yield None
        return self._view()
