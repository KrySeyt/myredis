from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.wait_replicas import WaitReplicas as WaitReplicasInteractor

T_co = TypeVar("T_co", covariant=True)


class WaitReplicas(Generic[T_co]):
    def __init__(self, interactor: WaitReplicasInteractor, presenter: Callable[[int], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self, replicas_count: int, timeout: int) -> Coroutine[T_co]:
        responded_replicas_count = yield from self._interactor(replicas_count, timeout / 1000)
        return self._presenter(responded_replicas_count)
