from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.get_config import GetConfig as GetConfigInteractor

T_co = TypeVar("T_co", covariant=True)


class GetConfig(Generic[T_co]):
    def __init__(self, interactor: GetConfigInteractor, presenter: Callable[[str, Any], T_co]) -> None:
        self._interactor = interactor
        self._presenter = presenter

    def __call__(self, key: str) -> Coroutine[T_co]:
        val = yield from self._interactor(key)
        return self._presenter(key, val)
