from abc import ABC, abstractmethod
from typing import Any

from myasync import Coroutine


class ConfigGateway(ABC):
    @abstractmethod
    def get(self, key: str) -> Coroutine[Any]:
        raise NotImplementedError
