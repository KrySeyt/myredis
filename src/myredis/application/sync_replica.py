from myredis.application.gateways.values import ValuesStorage
from myredis.domain.record import Record


class SyncReplica:
    def __init__(self, values_storage: ValuesStorage) -> None:
        self._values_storage = values_storage

    def __call__(self) -> dict[str, Record]:  # TODO: Better send file instead of Records
        return self._values_storage.get_all()
