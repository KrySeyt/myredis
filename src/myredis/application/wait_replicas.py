from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.replicas import ReplicasManager

T_co = TypeVar("T_co")


class WaitReplicas(Generic[T_co]):
    def __init__(self, replicas: ReplicasManager, presenter: Callable[[int], T_co]) -> None:
        self._replicas = replicas
        self._presenter = presenter

    def __call__(self, replicas_count: int, timeout: float) -> Coroutine[T_co]:
        responded_replicas_count = yield from self._replicas.wait(replicas_count, timeout)
        return self._presenter(responded_replicas_count)
