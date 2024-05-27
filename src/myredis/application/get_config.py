from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.config import ConfigGateway
from myredis.domain.key import Key

T = TypeVar("T")


class GetConfig(Generic[T]):
    def __init__(self, config: ConfigGateway, view: Callable[[str, str | None], T]) -> None:
        self._config = config
        self._view = view

    def __call__(self, key: Key) -> Coroutine[T]:
        config_value = yield from self._config.get(key)

        if config_value is not None:
            config_value = str(config_value)

        return self._view(key, config_value)
