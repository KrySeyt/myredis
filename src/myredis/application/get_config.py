from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.domain.key import Key

ViewT = TypeVar("ViewT")


class GetConfigParam(Generic[ViewT]):
    def __init__(self, config: dict[Key, str | int], view: Callable[[str, str | None], ViewT]) -> None:
        self._config = config
        self._view = view

    def __call__(self, key: Key) -> Coroutine[ViewT]:
        yield None

        value = self._config.get(key, None)

        if value is not None:
            value = str(value)

        return self._view(key, value)
