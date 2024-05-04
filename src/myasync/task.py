from __future__ import annotations
from typing import TypeVar

from myasync import (
    AbstractTask,
    Await,
    Coroutine,
)

T_co = TypeVar("T_co", covariant=True)


class Task(AbstractTask[T_co]):
    def __init__(self, coro: Coroutine[T_co]) -> None:
        self._coro = coro
        self._is_completed = False
        self._result: T_co | None = None

    @property
    def result(self) -> T_co | None:
        return self._result

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    def __next__(self) -> Await | None:
        try:
            return next(self._coro)
        except StopIteration as err:
            self._is_completed = True
            self._result = err.value
            raise


class TaskProxy(AbstractTask[T_co]):
    def __init__(self, task: AbstractTask[T_co]) -> None:
        self._task = task

    @property
    def result(self) -> T_co | None:
        return self._task.result

    @property
    def is_completed(self) -> bool:
        return self._task.is_completed

    def __next__(self) -> Await | None:
        if self._task.is_completed:
            raise StopIteration(self._task.result)

        return None
