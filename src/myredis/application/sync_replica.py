from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.record import Record

T_co = TypeVar("T_co")


class SyncReplica(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, view: Callable[[dict[str, Record[Any]]], T_co]) -> None:
        self._values_storage = values_storage
        self._view = view

    def __call__(self) -> Coroutine[T_co]:  # TODO: Better send file instead of Records
        records = yield from self._values_storage.get_all()
        return self._view(records)
