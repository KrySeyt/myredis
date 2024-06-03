from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.replicas import ReplicasManager
from myredis.application.interfaces.values import Values
from myredis.domain.key import Key
from myredis.domain.record import Record

ViewT = TypeVar("ViewT")


class Set(Generic[ViewT]):
    def __init__(self, values_storage: Values, replicas: ReplicasManager, view: Callable[[], ViewT]) -> None:
        self._values_storage = values_storage
        self._replicas = replicas
        self._view = view

    def __call__(self, key: Key, record: Record[Any]) -> Coroutine[ViewT]:
        yield from self._values_storage.set(key, record)
        yield from self._replicas.set(key, record)
        return self._view()
