from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

T_co = TypeVar("T_co")


class Get(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, presenter: Callable[[Record | None], T_co]) -> None:
        self._values_storage = values_storage
        self._presenter = presenter

    def __call__(self, key: Key) -> Coroutine[T_co]:
        record = yield from self._values_storage.get(key)
        return self._presenter(record)
