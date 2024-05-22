from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.replicas import ReplicasManager
from myredis.application.gateways.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record

T_co = TypeVar("T_co")


class Set(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, replicas: ReplicasManager, presenter: Callable[[], T_co]) -> None:
        self._values_storage = values_storage
        self._replicas = replicas
        self._presenter = presenter

    def __call__(self, key: Key, record: Record) -> Coroutine[T_co]:
        yield from self._values_storage.set(key, record)
        yield from self._replicas.set(key, record)
        return self._presenter()
