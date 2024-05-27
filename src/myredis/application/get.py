from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

T = TypeVar("T")


class Get(Generic[T]):
    def __init__(self, values_storage: ValuesStorage, view: Callable[[Record[Any] | None], T]) -> None:
        self._values_storage = values_storage
        self._view = view

    def __call__(self, key: Key) -> Coroutine[T]:
        record = yield from self._values_storage.get(key)
        return self._view(record)
