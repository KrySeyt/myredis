from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.record import Record

T = TypeVar("T")


class SyncReplica(Generic[T]):
    def __init__(self, values_storage: ValuesStorage, view: Callable[[dict[str, Record[Any]]], T]) -> None:
        self._values_storage = values_storage
        self._view = view

    def __call__(self) -> Coroutine[T]:
        records = yield from self._values_storage.pop_new()
        return self._view(records)
