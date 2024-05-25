from typing import Collection


def none() -> bytes:
    return "$-1\r\n".encode('utf-8')


def int_(value: int) -> bytes:
    return f":{value}\r\n".encode("utf-8")


def str_(value: str) -> bytes:
    return f"+{value}\r\n".encode("utf-8")


def bulk_str(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode()


def array_(*serialized_values: bytes) -> bytes:
    return "".encode("utf-8").join((f"*{len(serialized_values)}\r\n".encode("utf-8"), *serialized_values))
