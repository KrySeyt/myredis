from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.values import ValuesStorage
from myredis.domain.record import Record

T_co = TypeVar("T_co")


class SyncReplica(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, presenter: Callable[[dict[str, Record]], T_co]) -> None:
        self._values_storage = values_storage
        self._presenter = presenter

    def __call__(self) -> Coroutine[T_co]:  # TODO: Better send file instead of Records
        records = yield from self._values_storage.get_all()
        return self._presenter(records)
