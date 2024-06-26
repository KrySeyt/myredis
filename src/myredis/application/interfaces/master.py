from abc import ABC, abstractmethod
from typing import Any

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class MasterSentWrongDataError(ValueError):
    pass


class Master(ABC):
    @abstractmethod
    def get_records(self) -> Coroutine[dict[Key, Record[Any]]]:
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> Coroutine[str]:
        raise NotImplementedError
