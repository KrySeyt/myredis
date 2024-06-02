from typing import Any

from tests.serializers import bulk_str, array_


def ok() -> bytes:
    return "+OK\r\n".encode("utf-8")


def get(value: Any) -> bytes:
    return f"${len(str(value))}\r\n{value}\r\n".encode("utf-8")


def not_found() -> bytes:
    return "$-1\r\n".encode("utf-8")


def pong() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode("utf-8")


def config_param(key: str, value: str | None) -> bytes:
    if value is None:
        serialized_value = not_found()

    elif isinstance(value, str):
        serialized_value = bulk_str(value)

    else:
        raise ValueError(value)

    return array_(bulk_str(key), serialized_value)


def wait(replicas_count: int) -> bytes:
    return f":{replicas_count}\r\n".encode("utf-8")
