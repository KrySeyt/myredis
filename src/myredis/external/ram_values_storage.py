from copy import deepcopy
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.values import Values
from myredis.domain.key import Key
from myredis.domain.record import Record

storage: dict[Key, Record[Any]] = {}
new: dict[Key, Record[Any]] = {}


class RAMValues(Values):
    def set(self, key: Key, record: Record[Any]) -> Coroutine[None]:
        yield None

        storage[key] = record
        new[key] = record

    def set_records(self, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        yield None

        storage.clear()
        storage.update(records)

    def get(self, key: Key) -> Coroutine[Record[Any] | None]:
        yield None

        record = storage.get(key)
        return record

    def pop_new(self) -> Coroutine[dict[Key, Record[Any]]]:
        global new  # noqa: PLW0603
        yield None

        new_records = new
        new = {}
        return new_records

    def get_records(self) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        return deepcopy(storage)
