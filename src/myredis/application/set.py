from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import ReplicasManager
from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

T_co = TypeVar("T_co")


class Set(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, replicas: ReplicasManager, view: Callable[[], T_co]) -> None:
        self._values_storage = values_storage
        self._replicas = replicas
        self._view = view

    def __call__(self, key: Key, record: Record) -> Coroutine[T_co]:
        yield from self._values_storage.set(key, record)
        yield from self._replicas.set(key, record)
        return self._view()
