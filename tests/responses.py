from typing import Any


def ok() -> bytes:
    return "+OK\r\n".encode("utf-8")


def get(value: Any) -> bytes:
    if isinstance(value, str):
        return f"+{value}\r\n".encode("utf-8")

    if isinstance(value, int):
        return f":{value}\r\n".encode("utf-8")

    raise ValueError(value)


def not_found() -> bytes:
    return ":-1\r\n".encode("utf-8")


def pong() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode("utf-8")


def config_param(key: str, value: Any) -> bytes:
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(value))}\r\n{value}\r\n".encode("utf-8")


def wait(replicas_count: int) -> bytes:
    return f":{replicas_count}\r\n".encode("utf-8")
