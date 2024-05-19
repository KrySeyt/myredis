from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.ack import Ack as AckInteractor


class Ack:
    def __init__(self, interactor: AckInteractor) -> None:
        self._interactor = interactor

    def __call__(self) -> Coroutine[bytes]:
        yield from self._interactor()
        return responses.ack()
