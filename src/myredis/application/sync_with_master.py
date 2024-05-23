from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.master import Master
from myredis.application.gateways.values import ValuesStorage

T_co = TypeVar("T_co")


class SyncWithMaster(Generic[T_co]):
    def __init__(self, values_storage: ValuesStorage, master_gateway: Master, view: Callable[[], T_co]) -> None:
        self._values_storage = values_storage
        self._master_gateway = master_gateway
        self._view = view

    def __call__(self) -> Coroutine[T_co]:
        records = yield from self._master_gateway.get_records()
        yield from self._values_storage.set_records(records)
        return self._view()
