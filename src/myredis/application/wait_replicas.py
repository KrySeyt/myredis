from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import ReplicasManager

T_co = TypeVar("T_co")


class WaitReplicas(Generic[T_co]):
    def __init__(self, replicas: ReplicasManager, view: Callable[[int], T_co]) -> None:
        self._replicas = replicas
        self._view = view

    def __call__(self, replicas_count: int, timeout: float) -> Coroutine[T_co]:
        responded_replicas_count = yield from self._replicas.wait(replicas_count, timeout)
        return self._view(responded_replicas_count)
