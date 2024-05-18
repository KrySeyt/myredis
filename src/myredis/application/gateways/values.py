from abc import ABC, abstractmethod

from myredis.domain.key import Key
from myredis.domain.record import Record


class ValuesStorage(ABC):
    @abstractmethod
    def set(self, key: Key, record: Record) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_records(self, records: dict[Key, Record]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Key) -> Record | None:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> dict[Key, Record]:
        raise NotImplementedError
