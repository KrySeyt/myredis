from abc import ABC, abstractmethod

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class MasterSentWrongData(ValueError):
    pass


class Master(ABC):
    @abstractmethod
    def get_records(self) -> Coroutine[dict[Key, Record]]:
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> Coroutine[str]:
        raise NotImplementedError
