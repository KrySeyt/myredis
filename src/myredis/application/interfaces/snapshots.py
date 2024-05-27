from abc import ABC, abstractmethod
from typing import Any

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class Snapshots(ABC):
    @abstractmethod
    def create(self, name: str, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def read(self, name: str) -> Coroutine[dict[Key, Record[Any]]]:
        raise NotImplementedError
