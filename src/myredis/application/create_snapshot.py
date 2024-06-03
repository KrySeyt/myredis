from pathlib import Path
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.snapshots import Snapshots
from myredis.application.interfaces.values import Values

ViewT = TypeVar("ViewT")


class CreateSnapshot(Generic[ViewT]):
    def __init__(self, values: Values, snapshots: Snapshots) -> None:
        self._values = values
        self._snapshots = snapshots

    def __call__(self, snapshot_path: Path) -> Coroutine[None]:
        records = yield from self._values.pop_new()
        yield from self._snapshots.create(snapshot_path, records)
