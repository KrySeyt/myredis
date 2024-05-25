from typing import Any

from myredis.domain.key import Key
from myredis.domain.record import Record


def none() -> bytes:
    return b"$-1\r\n"


def int_(value: int) -> bytes:
    return f":{value}\r\n".encode()


def str_(value: str) -> bytes:
    return f"+{value}\r\n".encode()


def bulk_str(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode()


def array_(*serialized_values: bytes) -> bytes:
    return b"".join((f"*{len(serialized_values)}\r\n".encode(), *serialized_values))


def record(key: Key, record_: Record[Any]) -> bytes:
    return (
        f"+{key}\r\n"
        f"+{record_.value}\r\n"
        f":{record_.expires if record_.expires else -1}\r\n"
    ).encode()


def records(*serialized_values: bytes) -> bytes:
    return b"".join((f"SYNC%{len(serialized_values)}\r\n".encode(), *serialized_values))
