import copy
import time

from myredis.application.gateways.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record


class RAMValuesStorage(ValuesStorage):
    def __init__(self) -> None:
        self._storage: dict[Key, Record] = {}

    def set(self, key: Key, record: Record) -> None:
        self._storage[key] = record

    def get(self, key: Key) -> Record | None:
        record = self._storage.get(key, None)

        if record is None:
            return None

        if record.expires and record.expires < time.time():
            return None

        return record

    def get_all(self) -> dict[Key, Record]:
        return copy.deepcopy(self._storage)
