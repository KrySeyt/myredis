import argparse
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

@dataclass
class Record:
    value: Any
    expire: float | None


COMMANDS = {"PING", "ECHO", "SET", "PX", "GET", "INFO", "REPLICATION"}

storage: dict[str, Any] = dict()


def commands_handler(conn: socket.socket) -> None:
    while command := conn.recv(1024):
        parsed_command = parse_redis_command(command)
        match parsed_command:
            case ["PING"]:
                conn.send(ping())

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
                print(parsed_command)


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
    return "$11\r\nrole:master\r\n".encode("utf-8")


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="My Redis")
    arg_parser.add_argument("--port", default=6379, type=int)
    args = arg_parser.parse_args()

    server_socket = socket.create_server(("localhost", args.port), reuse_port=True)

    with ThreadPoolExecutor() as pool:
        while True:
            conn, _ = server_socket.accept()
            pool.submit(commands_handler, conn)


if __name__ == "__main__":
    main()
