from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.ping import Ping as PingInteractor

T_co = TypeVar("T_co", covariant=True)


class Ping(Generic[T_co]):
    def __init__(self, interactor: PingInteractor, presenter: Callable[[], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self) -> Coroutine[T_co]:
        yield from self._interactor()
        return self._presenter()
