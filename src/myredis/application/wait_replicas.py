from myasync import Coroutine

from myredis.application.gateways.replicas import ReplicasManager


class WaitReplicas:
    def __init__(self, replicas: ReplicasManager) -> None:
        self._replicas = replicas

    def __call__(self, replicas_count: int, timeout: float) -> Coroutine[int]:
        responded_replicas_count = yield from self._replicas.wait(replicas_count, timeout)
        return responded_replicas_count
