from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.replicas import Replica, ReplicasManager

T_co = TypeVar("T_co")


class AddReplica(Generic[T_co]):
    def __init__(self, replicas: ReplicasManager, presenter: Callable[[], T_co]) -> None:
        self._replicas = replicas
        self._presenter = presenter

    def __call__(self, replica: Replica) -> Coroutine[T_co]:
        yield from self._replicas.add_replica(replica)
        return self._presenter()
