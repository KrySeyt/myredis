from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import Replica, ReplicasManager

ViewT = TypeVar("ViewT")


class AddReplica(Generic[ViewT]):
    def __init__(self, replicas: ReplicasManager, view: Callable[[], ViewT]) -> None:
        self._replicas = replicas
        self._view = view

    def __call__(self, replica: Replica) -> Coroutine[ViewT]:
        yield from self._replicas.add_replica(replica)
        return self._view()
