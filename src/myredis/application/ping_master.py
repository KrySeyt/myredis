from myasync import Coroutine

from myredis.application.interfaces.master import Master


class PingMaster:
    def __init__(self, master: Master) -> None:
        self._master = master

    def __call__(self) -> Coroutine[None]:
        yield from self._master.ping()
