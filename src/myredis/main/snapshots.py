import logging
from pathlib import Path
from typing import Any

import myasync
from myasync import Coroutine

from myredis.application.create_snapshot import CreateSnapshot

logger = logging.getLogger(__name__)


def create_snapshot_worker(
        snapshot_path: Path,
        interval: float,
        create_snapshot: CreateSnapshot[Any],
) -> Coroutine[None]:
    while True:
        yield from myasync.sleep(interval)
        yield from myasync.run_in_thread(create_snapshot(snapshot_path))
        logger.info(f"Snapshot created: {snapshot_path}")
