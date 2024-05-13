from typing import Any

from myredis.application.gateways.values import ValuesStorage


class Set:
    def __init__(self, values_storage: ValuesStorage) -> None:
        self._values_storage = values_storage

    def __call__(self, key: str, value: object, expire_time: int | None = None) -> None:
        """
        :param key:
        :param value:
        :param expire_time: expire time in milliseconds
        :return:
        """

        return self._values_storage.set(key, value, expire_time)
