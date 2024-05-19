from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.get_config import GetConfig as GetConfigInteractor
from myredis.external.config import Config


# Temp
class ConfigVar:
    config: Config | None = None

    @classmethod
    def set(cls, config: Config) -> None:
        cls.config = config

    @classmethod
    def get(cls) -> Config:
        assert cls.config is not None
        return cls.config


class GetConfig:
    def __init__(self, interactor: GetConfigInteractor) -> None:
        self._interactor = interactor

    def __call__(self, key: str) -> Coroutine[bytes]:
        val = yield from self._interactor(key)
        return responses.config_param(key, val)
