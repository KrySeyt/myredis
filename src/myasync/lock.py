from __future__ import annotations

from myasync import Coroutine


class Lock:
    def __init__(self) -> None:
        self._locked = False

    def acquire(self) -> Coroutine[None]:
        while self._locked:
            yield None

        self._locked = True

    def release(self) -> None:
        assert self._locked
        self._locked = False
