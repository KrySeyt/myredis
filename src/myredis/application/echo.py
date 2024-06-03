from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

ValueT = TypeVar("ValueT")
ViewT = TypeVar("ViewT")


class Echo(Generic[ViewT]):
    def __init__(self, view: Callable[[ValueT], ViewT]) -> None:
        self._view = view

    def __call__(self, value: ValueT) -> Coroutine[ViewT]:
        yield None
        return self._view(value)
