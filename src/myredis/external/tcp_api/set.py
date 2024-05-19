import time

from myasync import Coroutine

from myredis.application.set import Set
from myredis.domain.record import Record
from myredis.external import responses
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_replicas import TCPReplicasManager


def set_(key: str, value: object, expire: int | None = None) -> Coroutine[bytes]:
    interactor = Set(RAMValuesStorage(), TCPReplicasManager())
    yield from interactor(
        key,
        Record(
            value,
            time.time() + expire / 1000 if expire is not None else None,
        ),
    )
    return responses.ok()
