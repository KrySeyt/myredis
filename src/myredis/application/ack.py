from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

T_co = TypeVar("T_co")


class Ack(Generic[T_co]):
    def __init__(self, presenter: Callable[[], T_co]) -> None:
        self._presenter = presenter

    def __call__(self) -> Coroutine[T_co]:
        yield None
        return self._presenter()
