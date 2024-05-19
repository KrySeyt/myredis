from myasync import Coroutine

from myredis.application.get_config import GetConfig
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


def config_get(key: str) -> Coroutine[bytes]:
    get_config_interactor = GetConfig(ConfigVar.get())
    val = yield from get_config_interactor(key)
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(val))}\r\n{val}\r\n".encode()
