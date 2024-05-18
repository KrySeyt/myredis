import socket
from abc import ABC, abstractmethod

from myasync import Coroutine


class ReplicaSentWrongData(ValueError):
    pass


class Replicas(ABC):
    @abstractmethod
    def wait(self, replicas_count: int, timeout: float) -> Coroutine[int]:
        raise NotImplementedError

    # TODO: Replace socket with abstraction
    @abstractmethod
    def add_replica(self, replica_conn: socket.socket) -> Coroutine[None]:
        raise NotImplementedError
