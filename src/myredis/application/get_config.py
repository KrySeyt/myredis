from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.gateways.config import ConfigGateway
from myredis.domain.key import Key

T_co = TypeVar("T_co")


class GetConfig(Generic[T_co]):
    def __init__(self, config: ConfigGateway, view: Callable[[str, Any], T_co]) -> None:
        self._config = config
        self._view = view

    def __call__(self, key: Key) -> Coroutine[T_co]:
        config_value = yield from self._config.get(key)
        return self._view(key, config_value)
