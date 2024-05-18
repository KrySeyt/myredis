from abc import ABC, abstractmethod

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class MasterGateway(ABC):
    @abstractmethod
    def get_records(self) -> Coroutine[dict[Key, Record]]:
        raise NotImplementedError

