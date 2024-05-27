from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import ReplicasManager

T = TypeVar("T")


class WaitReplicas(Generic[T]):
    def __init__(self, replicas: ReplicasManager, view: Callable[[int], T]) -> None:
        self._replicas = replicas
        self._view = view

    def __call__(self, replicas_count: int, timeout: float) -> Coroutine[T]:
        responded_replicas_count = yield from self._replicas.wait(replicas_count, timeout)
        return self._view(responded_replicas_count)
