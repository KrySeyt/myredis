import csv
import os.path
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.snapshots import Snapshots
from myredis.domain.key import Key
from myredis.domain.record import Record


class DiskSnapshots(Snapshots):
    def create(self, snapshot_path: str, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        yield None

        file_exists = os.path.exists(snapshot_path)

        with open(snapshot_path, "a") as file:
            writer = csv.DictWriter(file, ["key", "value", "expires"])

            if not file_exists:
                writer.writeheader()

            for key, record in records.items():
                writer.writerow({
                    "key": key,
                    "value": record.value,
                    "expires": record.expires,
                })

    def read(self, snapshot_path: str) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        records: dict[Key, Record[Any]] = {}
        with open(snapshot_path) as file:
            reader = csv.DictReader(file)
            for row in reader:
                records[row["key"]] = Record(
                    row["value"],
                    float(row["expires"]) if row["expires"] else None,
                )

        return records
