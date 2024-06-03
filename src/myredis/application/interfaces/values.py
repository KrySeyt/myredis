from abc import ABC, abstractmethod
from typing import Any

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class Values(ABC):
    @abstractmethod
    def set(self, key: Key, record: Record[Any]) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def set_records(self, records: dict[Key, Record[Any]]) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Key) -> Coroutine[Record[Any] | None]:
        raise NotImplementedError

    @abstractmethod
    def pop_new(self) -> Coroutine[dict[Key, Record[Any]]]:
        raise NotImplementedError
