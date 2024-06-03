import time
from dataclasses import dataclass
from typing import Generic, NewType, TypeVar

T = TypeVar("T")

Milliseconds = NewType("Milliseconds", int)
Seconds = NewType("Seconds", float)


class Expired:
    pass


@dataclass(frozen=True)
class Record(Generic[T]):
    _value: T
    expires: Seconds | None = None

    @property
    def value(self) -> T | Expired:
        if self.is_expired():
            return Expired()

        return self._value

    def is_expired(self) -> bool:
        if self.expires is not None and self.expires < time.time():
            return True

        return False
