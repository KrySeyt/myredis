from typing import Any

from myasync import Coroutine

from myredis.application.ping_master import PingMaster
from myredis.application.sync_with_master import SyncWithMaster


def sync_with_master(ping_master: PingMaster, sync_with_master_interactor: SyncWithMaster[Any]) -> Coroutine[None]:
    yield from ping_master()
    yield from sync_with_master_interactor()
