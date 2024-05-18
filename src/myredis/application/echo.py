from typing import Any

from myasync import Coroutine

from myredis.application.gateways.values import ValuesStorage


class Echo:
    def __call__(self, value: str) -> Coroutine[str]:
        yield None
        return value
