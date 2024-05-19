from typing import Any


def set_(key: str, value: Any, expire: int | None = None) -> bytes:
    """
    :param key:
    :param value:
    :param expire: expire time in milliseconds
    :return:
    """

    if expire is None:
        return (
            f"*3\r\n"
            f"$3\r\nSET\r\n"
            f"${len(key)}\r\n{key}\r\n"
            f"${len(str(value))}\r\n{value}\r\n"
        ).encode()

    return (
        f"*5\r\n"
        f"$3\r\nSET\r\n"
        f"${len(key)}\r\n{key}\r\n"
        f"${len(str(value))}\r\n{value}\r\n"
        f"$2\r\nPX\r\n"
        f"${len(str(expire))}\r\n{expire}\r\n"
    ).encode()


def get(key: str) -> bytes:
    return (
        f"*2\r\n"
        f"$3\r\nGET\r\n"
        f"${len(key)}\r\n{key}\r\n"
    ).encode()


def ping() -> bytes:
    return (
        b"*1\r\n"
        b"$4\r\nPING\r\n"
    )


def echo(value: str) -> bytes:
    return (
        f"*2\r\n"
        f"$4\r\nECHO\r\n"
        f"${len(value)}\r\n{value}\r\n"
    ).encode()


def config_get(key: str) -> bytes:
    return (
        f"*3\r\n"
        f"$6\r\nCONFIG\r\n"
        f"$3\r\nGET\r\n"
        f"${len(key)}\r\n{key}\r\n"
    ).encode()


def wait(replicas_count: int, expire: int) -> bytes:
    return (
        f"*3\r\n"
        f"$4\r\nWAIT\r\n"
        f"${len(str(replicas_count))}\r\n{replicas_count}\r\n"
        f"${len(str(expire))}\r\n{expire}\r\n"
    ).encode()


def replica_sync() -> bytes:
    return (
        b"*2\r\n"
        b"$7\r\n"
        b"REPLICA\r\n"
        b"$4\r\n"
        b"SYNC\r\n"
    )


def replica_get_ack() -> bytes:
    return (
        b"*2\r\n"
        b"$8\r\n"
        b"REPLCONF\r\n"
        b"$6\r\n"
        b"GETACK\r\n"
    )
