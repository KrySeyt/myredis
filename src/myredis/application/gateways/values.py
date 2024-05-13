from abc import ABC, abstractmethod
from typing import Any


class ValuesStorage(ABC):
    @abstractmethod
    def get(self, key: str) -> object | None:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any, expire_time: int | None) -> None:
        """
        :param key:
        :param value:
        :param expire_time: expire time in milliseconds
        :return:
        """

        raise NotImplementedError
