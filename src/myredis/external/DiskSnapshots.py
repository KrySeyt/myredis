import json
from dataclasses import asdict
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.snapshots import Snapshots
from myredis.domain.key import Key
from myredis.domain.record import Record


class DiskSnapshots(Snapshots):
    def create(self, name: str, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        yield None

        data = {}
        for key, record in records.items():
            data[key] = asdict(record)

        with open(name, "w") as file:
            file.write(json.dumps(data))

    def read(self, name: str) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        with open(name, "rb") as file:
            records_data = json.load(file)

        records = {}
        for key, record_data in records_data.items():
            records[key] = Record(**record_data)

        return records
