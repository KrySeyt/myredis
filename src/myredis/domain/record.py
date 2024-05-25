import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Record(Generic[T]):
    """
    :param expires: expire time in seconds. None is never
    """

    _value: T
    expires: float | None = None

    @property
    def value(self) -> object:
        if self.expires is not None and self.expires < time.time():
            return None

        return self._value
