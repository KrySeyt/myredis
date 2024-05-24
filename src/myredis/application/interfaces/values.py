from abc import ABC, abstractmethod

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class ValuesStorage(ABC):
    @abstractmethod
    def set(self, key: Key, record: Record) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def set_records(self, records: dict[Key, Record]) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Key) -> Coroutine[Record | None]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Coroutine[dict[Key, Record]]:
        raise NotImplementedError
