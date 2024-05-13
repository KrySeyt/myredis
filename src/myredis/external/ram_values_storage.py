import time
from dataclasses import dataclass

from myredis.application.gateways.values import ValuesStorage


@dataclass
class Record:
    """
    :param expires: expire time in seconds
    """

    value: object
    expires: float | None = None


class RAMValuesStorage(ValuesStorage):
    def __init__(self) -> None:
        self._storage: dict[str, Record] = {}

    def set(self, key: str, value: object, expire_time: int | None = None) -> None:
        expire_time_seconds = time.time() + expire_time / 1000 if expire_time else None
        self._storage[key] = Record(value, expire_time_seconds)

    def get(self, key: str) -> object | None:
        record = self._storage.get(key, None)

        if record is None:
            return None

        if record.expires and record.expires < time.time():
            return None

        return record.value
