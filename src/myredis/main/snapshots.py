from typing import Any

import myasync
from myasync import Coroutine

from myredis.application.create_snapshot import CreateSnapshot


def create_snapshot_worker(
        snapshot_path: str,
        interval: float,
        create_snapshot: CreateSnapshot[Any],
) -> Coroutine[None]:
    while True:
        yield from myasync.sleep(interval)
        yield from create_snapshot(snapshot_path)
        print(f"Snapshot created: {snapshot_path}")
