from typing import Any

from myredis.domain.record import Record


def ok() -> bytes:
    return b"+OK\r\n"


def get(record: Record | None) -> bytes:
    if not record:
        return not_found()

    value = record.value

    if isinstance(value, str):
        return f"+{value}\r\n".encode()

    if isinstance(value, int):
        return f":{value}\r\n".encode()

    raise ValueError(record)


def not_found() -> bytes:
    return b":-1\r\n"


def pong() -> bytes:
    return b"+PONG\r\n"


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode()


def config_param(key: str, value: Any) -> bytes:
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(value))}\r\n{value}\r\n".encode()


def wait(replicas_count: int) -> bytes:
    return f":{replicas_count}\r\n".encode()


def ack() -> bytes:
    return b"*2\r\n$8\r\nREPLCONF\r\n$3\r\nACK\r\n"


def records(records: dict[str, Record]) -> bytes:
    command = [f"SYNC%{len(records)}\r\n"]
    for key, record in records.items():
        command.append(
            f"+{key}\r\n"
            f"+{record.value}\r\n"
            f":{record.expires if record.expires else -1}\r\n",
        )

    return "".join(command).encode("utf-8")
