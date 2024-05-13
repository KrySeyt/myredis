from typing import Any


def ok() -> bytes:
    return b"+OK\r\n"


def str_(value: str) -> bytes:
    return f"+{value}\r\n".encode()


def not_found() -> bytes:
    return b"+-1\r\n"


def pong() -> bytes:
    return b"+PONG\r\n"


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode()


def config_param(key: str, value: Any) -> bytes:
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(value))}\r\n{value}\r\n".encode()


def wait(replicas_count: int) -> bytes:
    return f":{replicas_count}\r\n".encode()
