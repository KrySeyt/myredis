import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


class Expired:
    pass


@dataclass(frozen=True)
class Record(Generic[T]):
    """
    :param expires: expire time in seconds. None is never
    """

    _value: T
    expires: float | None = None

    @property
    def value(self) -> T | Expired:
        if self.is_expired():
            return Expired()

        return self._value

    def is_expired(self) -> bool:
        if self.expires is not None and self.expires < time.time():
            return True

        return False
