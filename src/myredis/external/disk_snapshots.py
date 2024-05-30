import csv
from pathlib import Path
from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.snapshots import Snapshots
from myredis.domain.key import Key
from myredis.domain.record import Record


class DiskSnapshots(Snapshots):
    def create(self, snapshot_path: Path, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        yield None

        file_existed = snapshot_path.exists()

        with snapshot_path.open("a") as file:
            writer = csv.DictWriter(file, ["key", "value", "expires"])

            if not file_existed:
                writer.writeheader()

            for key, record in records.items():
                if record.is_expired():
                    continue

                writer.writerow({
                    "key": key,
                    "value": record.value,
                    "expires": record.expires,
                })

    def read(self, snapshot_path: Path) -> Coroutine[dict[Key, Record[Any]]]:
        yield None

        records: dict[Key, Record[Any]] = {}
        with snapshot_path.open("r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                expires = row["expires"]
                record = Record(
                    row["value"],
                    float(expires) if expires else None,
                )

                if record.is_expired():
                    continue

                records[row["key"]] = record

        return records
