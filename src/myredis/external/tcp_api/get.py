from myasync import Coroutine

from myredis.application.get import Get
from myredis.external.ram_values_storage import RAMValuesStorage


def get(key: str) -> Coroutine[bytes]:
    interactor = Get(RAMValuesStorage())
    record = yield from interactor(key)
    value = record.value if record is not None else -1
    return f"+{value}\r\n".encode()
