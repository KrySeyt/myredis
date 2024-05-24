from typing import Any

from myasync import Coroutine

from myredis.application.interfaces.config import ConfigGateway


class Config(ConfigGateway):
    def __init__(self, params: dict[str, Any]) -> None:
        self._params = params

    def get(self, key: str) -> Coroutine[Any]:
        yield None

        return self._params.get(key, None)
