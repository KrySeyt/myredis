from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.echo import Echo as EchoInteractor


class Echo:
    def __init__(self, interactor: EchoInteractor) -> None:
        self._interactor = interactor

    def __call__(self, input_str: str) -> Coroutine[bytes]:
        value = yield from self._interactor(input_str)
        return responses.echo(value)
