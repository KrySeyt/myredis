import copy
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

storage: dict[Key, Record[Any]] = {}
new: dict[Key, Record[Any]] = {}


class RAMValuesStorage(ValuesStorage):
    def set(self, key: Key, record: Record[Any]) -> Coroutine[None]:
        yield None

        storage[key] = record
        new[key] = record

    def set_records(self, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        global storage
        yield None

        storage = copy.deepcopy(records)

    def get(self, key: Key) -> Coroutine[Record[Any] | None]:
        yield None

        record = storage.get(key)
        return record

    def pop_new(self) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        new_records = copy.deepcopy(new)
        new.clear()
        return new_records
