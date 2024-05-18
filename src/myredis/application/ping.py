from typing import Any

from myasync import Coroutine

from myredis.application.gateways.values import ValuesStorage


class Ping:
    def __call__(self) -> Coroutine[str]:
        yield None
        return "PONG"
