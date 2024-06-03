from collections.abc import Callable
from typing import Any, Generic, TypeVar

from myasync import Coroutine

from myredis.application.interfaces.values import Values
from myredis.domain.key import Key
from myredis.domain.record import Record

ViewT = TypeVar("ViewT")


class Get(Generic[ViewT]):
    def __init__(self, values_storage: Values, view: Callable[[Record[Any] | None], ViewT]) -> None:
        self._values_storage = values_storage
        self._view = view

    def __call__(self, key: Key) -> Coroutine[ViewT]:
        record = yield from self._values_storage.get(key)
        return self._view(record)
