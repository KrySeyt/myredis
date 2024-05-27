from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.snapshots import Snapshots
from myredis.application.interfaces.values import ValuesStorage

T = TypeVar("T")


class CreateSnapshot(Generic[T]):
    def __init__(self, values_storage: ValuesStorage, snapshots: Snapshots) -> None:
        self._values_storage = values_storage
        self._snapshots = snapshots

    def __call__(self, name: str) -> Coroutine[None]:
        records = yield from self._values_storage.pop_new()
        yield from self._snapshots.create(name, records)
