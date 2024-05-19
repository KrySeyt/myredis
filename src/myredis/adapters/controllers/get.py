from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.get import Get as GetInteractor


class Get:
    def __init__(self, interactor: GetInteractor) -> None:
        self._interactor = interactor

    def __call__(self, key: str) -> Coroutine[bytes]:
        record = yield from self._interactor(key)
        value = record.value if record is not None else -1
        return responses.get(value)
