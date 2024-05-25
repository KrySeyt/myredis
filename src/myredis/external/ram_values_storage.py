import copy
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record


class RAMValuesStorage(ValuesStorage):
    _storage: dict[Key, Record[Any]] = {}

    def set(self, key: Key, record: Record[Any]) -> Coroutine[None]:
        yield None

        self._storage[key] = record

    def set_records(self, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        yield None

        self._storage = copy.deepcopy(records)

    def get(self, key: Key) -> Coroutine[Record[Any] | None]:
        yield None

        record = self._storage.get(key, None)

        if record is None:
            return None

        return record

    def get_all(self) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        return copy.deepcopy(self._storage)
