
from myasync import Coroutine

from myredis.application.gateways.replicas import ReplicasManager
from myredis.application.gateways.values import ValuesStorage
from myredis.domain.key import Key
from myredis.domain.record import Record


class Set:
    def __init__(self, values_storage: ValuesStorage, replicas: ReplicasManager) -> None:
        self._values_storage = values_storage
        self._replicas = replicas

    def __call__(self, key: Key, record: Record) -> Coroutine[None]:
        yield from self._values_storage.set(key, record)
        yield from self._replicas.set(key, record)
