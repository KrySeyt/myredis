import time

from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.set import Set as SetInteractor
from myredis.domain.record import Record


class Set:
    def __init__(self, interactor: SetInteractor) -> None:
        self._interactor = interactor

    def __call__(self, key: str, value: object, expire: int | None = None) -> Coroutine[bytes]:
        yield from self._interactor(
            key,
            Record(
                value,
                time.time() + expire / 1000 if expire is not None else None,
            ),
        )

        return responses.ok()
