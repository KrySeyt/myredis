from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.get import Get as GetInteractor

T_co = TypeVar("T_co", covariant=True)


class Get(Generic[T_co]):
    def __init__(self, interactor: GetInteractor, presenter: Callable[[Any], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self, key: str) -> Coroutine[T_co]:
        record = yield from self._interactor(key)
        value = record.value if record is not None else -1
        return self._presenter(value)
