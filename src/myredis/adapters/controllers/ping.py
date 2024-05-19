from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.ping import Ping as PingInteractor


class Ping:
    def __init__(self, interactor: PingInteractor) -> None:
        self._interactor = interactor

    def __call__(self) -> Coroutine[bytes]:
        yield from self._interactor()
        return responses.pong()
