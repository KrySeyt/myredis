from argparse import ArgumentParser, Namespace
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import uuid4


@dataclass
class Record:
    value: Any
    expire: float | None


class Role(StrEnum):
    MASTER = "master"
    SLAVE = "slave"


COMMANDS = {"PING", "ECHO", "SET", "PX", "GET", "INFO", "REPLICATION"}
role: Role | None = None

replication_id = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
replication_offset = 0

storage: dict[str, Any] = dict()


def commands_handler(conn: socket.socket) -> None:
    while True:
        data = conn.recv(1024)

        if not data:
            continue

        parsed_command = parse_redis_command(data)
        print(f"{role}: Received command - {parsed_command}")
        match parsed_command:
            case ["PING"]:
                conn.sendall(ping())

            case ["ECHO", str(value)]:
                conn.send(echo(value))

            case ["SET", str(key), str(value), "PX", int(expire)]:
                conn.send(set_(key, value, expire=expire))

            case ["SET", str(key), str(value)]:
                conn.send(set_(key, value))

            case ["GET", str(key)]:
                conn.send(get(key))

            case ["INFO", "REPLICATION"]:
                conn.send(info())

            case _:
                print(f"{role}: Unknown command - {parsed_command}")


def parse_redis_command(serialized_command: bytes) -> list[Any]:
    decoded_command = serialized_command.decode("utf-8")
    commands: list[Any] = decoded_command.strip().split("\r\n")
    commands = [command for command in commands if command[0] not in ("*", "$")]
    for i, cmd in enumerate(commands):
        if cmd.upper() in COMMANDS:
            commands[i] = cmd.upper()

        elif cmd.isnumeric():
            commands[i] = int(cmd)

    return commands


def ping() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def set_(key: str, value: str, expire: int | None = None) -> bytes:
    expire_time = time.time() + expire / 1000 if expire is not None else None
    storage[key] = Record(value, expire_time)
    return "+OK\r\n".encode("utf-8")


def get(key: str) -> bytes:
    record = storage.get(key)

    if record is None:
        return "$-1\r\n".encode("utf-8")

    if record.expire is not None and record.expire < time.time():
        storage.pop(key)
        return "$-1\r\n".encode("utf-8")

    return f"+{record.value}\r\n".encode("utf-8")


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode("utf-8")


def info() -> bytes:
    data = f"role:{role}\r\nmaster_replid:{replication_id}\r\nmaster_repl_offset:{replication_offset}"
    return f"${len(data)}\r\n{data}\r\n".encode("utf-8")


def start_server(domain: str, port: int) -> None:
    server = socket.create_server((domain, port), reuse_port=True)

    with ThreadPoolExecutor() as pool:
        while True:
            conn, _ = server.accept()
            pool.submit(commands_handler, conn)


def main() -> None:
    global role

    arg_parser = ArgumentParser(description="My Redis")
    arg_parser.add_argument("--port", default=6379, type=int)
    arg_parser.add_argument("--replicaof", nargs=2, type=str)
    args = arg_parser.parse_args()

    if args.replicaof is not None:
        role = Role.SLAVE

        master_domain, master_port = args.replicaof
        master_port = int(master_port)
        master_conn = socket.create_connection((master_domain, master_port))
        master_conn.sendall("*1\r\n$4\r\nPING\r\n".encode("utf-8"))
        print(f"{role}: Master response - {master_conn.recv(1024).decode('utf-8')}")
        # master_conn.close()
        start_server("localhost", args.port)

    else:
        role = Role.MASTER
        start_server("localhost", args.port)


if __name__ == "__main__":
    main()
