import copy
import time

from myasync import Coroutine

from myredis.application.gateways.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record


class RAMValuesStorage(ValuesStorage):
    _storage: dict[Key, Record] = {}

    def set(self, key: Key, record: Record) -> Coroutine[None]:
        yield None

        self._storage[key] = record

    def set_records(self, records: dict[Key, Record]) -> Coroutine[None]:
        yield None

        self._storage = copy.deepcopy(records)

    def get(self, key: Key) -> Coroutine[Record | None]:
        yield None

        record = self._storage.get(key, None)

        if record is None:
            return None

        if record.expires and record.expires < time.time():
            return None

        return record

    def get_all(self) -> Coroutine[dict[Key, Record]]:
        yield None

        return copy.deepcopy(self._storage)
