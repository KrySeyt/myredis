from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.values import Values
from myredis.domain.record import Record

ViewT = TypeVar("ViewT")


class SyncReplica(Generic[ViewT]):
    def __init__(self, values_storage: Values, view: Callable[[dict[str, Record[Any]]], ViewT]) -> None:
        self._values_storage = values_storage
        self._view = view

    def __call__(self) -> Coroutine[ViewT]:
        records = yield from self._values_storage.get_records()
        return self._view(records)
