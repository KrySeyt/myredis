from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import ReplicasManager
from myredis.application.interfaces.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

T = TypeVar("T")


class Set(Generic[T]):
    def __init__(self, values_storage: ValuesStorage, replicas: ReplicasManager, view: Callable[[], T]) -> None:
        self._values_storage = values_storage
        self._replicas = replicas
        self._view = view

    def __call__(self, key: Key, record: Record[Any]) -> Coroutine[T]:
        yield from self._values_storage.set(key, record)
        yield from self._replicas.set(key, record)
        return self._view()
