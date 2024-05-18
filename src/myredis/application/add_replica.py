
from myasync import Coroutine

from myredis.application.gateways.replicas import Replica, ReplicasManager


class AddReplica:
    def __init__(self, replicas: ReplicasManager) -> None:
        self._replicas = replicas

    def __call__(self, replica: Replica) -> Coroutine[None]:
        yield from self._replicas.add_replica(replica)
