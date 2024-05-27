from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import Replica, ReplicasManager

T = TypeVar("T")


class AddReplica(Generic[T]):
    def __init__(self, replicas: ReplicasManager, view: Callable[[], T]) -> None:
        self._replicas = replicas
        self._view = view

    def __call__(self, replica: Replica) -> Coroutine[T]:
        yield from self._replicas.add_replica(replica)
        return self._view()
