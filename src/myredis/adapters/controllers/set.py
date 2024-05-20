import time
from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.set import Set as SetInteractor
from myredis.domain.record import Record

T_co = TypeVar("T_co", covariant=True)


class Set(Generic[T_co]):
    def __init__(self, interactor: SetInteractor, presenter: Callable[[], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self, key: str, value: object, expire: int | None = None) -> Coroutine[T_co]:
        yield from self._interactor(
            key,
            Record(
                value,
                time.time() + expire / 1000 if expire is not None else None,
            ),
        )

        return self._presenter()
