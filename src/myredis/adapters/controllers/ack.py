from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.ack import Ack as AckInteractor

T_co = TypeVar("T_co", covariant=True)


class Ack(Generic[T_co]):
    def __init__(self, interactor: AckInteractor, presenter: Callable[[], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self) -> Coroutine[T_co]:
        yield from self._interactor()
        return self._presenter()
