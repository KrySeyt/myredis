from typing import Any

from myasync import Coroutine

from myredis.application.gateways.config import ConfigGateway
from myredis.domain.key import Key


class GetConfig:
    def __init__(self, config: ConfigGateway) -> None:
        self._config = config

    def __call__(self, key: Key) -> Coroutine[Any]:
        config_value = yield from self._config.get(key)
        return config_value
