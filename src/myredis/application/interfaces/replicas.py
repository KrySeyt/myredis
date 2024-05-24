from abc import ABC, abstractmethod

from myasync import Coroutine

from myredis.domain.key import Key
from myredis.domain.record import Record


class ReplicaSentWrongDataError(ValueError):
    pass


class Replica(ABC):
    @abstractmethod
    def send(self, bytes_: bytes) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def recv(self, bytes_count: int) -> Coroutine[bytes]:
        raise NotImplementedError


class ReplicasManager(ABC):
    @abstractmethod
    def wait(self, replicas_count: int, timeout: float) -> Coroutine[int]:
        raise NotImplementedError

    @abstractmethod
    def add_replica(self, replica: Replica) -> Coroutine[None]:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: Key, record: Record) -> Coroutine[None]:
        raise NotImplementedError
