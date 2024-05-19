from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.wait_replicas import WaitReplicas as WaitReplicasInteractor


class WaitReplicas:
    def __init__(self, interactor: WaitReplicasInteractor) -> None:
        self._interactor = interactor

    def __call__(self, replicas_count: int, timeout: int) -> Coroutine[bytes]:
        responded_replicas_count = yield from self._interactor(replicas_count, timeout / 1000)
        return responses.wait(responded_replicas_count)
