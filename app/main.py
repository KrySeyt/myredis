import base64
import re
import threading
import traceback
from argparse import ArgumentParser
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable, Type


@dataclass
class Record:
    value: Any
    expire: float | None


class Role(StrEnum):
    MASTER = "master"
    SLAVE = "slave"


COMMANDS_TOKENS = {
    "PING",
    "ECHO",
    "SET",
    "PX",
    "GET",
    "INFO",
    "REPLICATION",
    "REPLCONF",
    "LISTENING-PORT",
    "CAPA",
    "EOF",
    "PSYNC2",
    "PSYNC",
    "GETACK",
}

role: Role | None = None

replication_id = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
replication_offset = 0
processed = 0
replicas = []

storage: dict[str, Any] = dict()


def resend_to_replicas(command: bytes) -> None:
    print(f"{role}: Replicas count - {len(replicas)}")
    for replica in replicas:
        replica.send(command)


def process_command(conn: socket.socket, command: list[Any], raw_cmd: bytes) -> None:
    global processed

    match command:
        case ["PING"]:
            if role == Role.MASTER:
                conn.sendall(ping())

        case ["ECHO", str(value)]:
            if role == Role.MASTER:
                conn.send(echo(value))

        case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
            resend_to_replicas(raw_cmd)
            response = set_(key, value, expire=expire)
            if role == Role.MASTER:
                conn.send(response)

        case ["SET", str(key), str(value) | int(value)]:
            resend_to_replicas(raw_cmd)
            response = set_(key, value)
            if role == Role.MASTER:
                conn.send(response)

        case ["GET", str(key)]:
            conn.send(get(key))

        case ["INFO", "REPLICATION"]:
            conn.send(info())

        case ["REPLCONF", "LISTENING-PORT", int(port)]:
            if role == Role.MASTER:
                conn.send(ok())

        case ["REPLCONF", "CAPA", "PSYNC2"]:
            if role == Role.MASTER:
                conn.send(ok())

        case ["PSYNC", *_]:
            if role == Role.MASTER:
                conn.send(full_resync())

                d = base64.b64decode(
                    "UkVESVMwMDEx+glyZWRpcy12ZXIFNy4yLjD6CnJlZGlzLWJpdHPAQPoFY3Rpb"
                    "WXCbQi8ZfoIdXNlZC1tZW3CsMQQAPoIYW9mLWJhc2XAAP/wbjv+wP9aog=="
                )

                conn.sendall(f"${len(d)}\r\n".encode("utf-8") + d)
                replicas.append(conn)

        case ["REPLCONF", "GETACK", "*"]:
            conn.send(ack())

        case _:
            print(f"{role}: Unknown command - {command}")

    processed += len(raw_cmd)


def commands_handler(conn: socket.socket) -> None:
    cmd_buffer = bytearray()
    while True:
        data = conn.recv(1024)

        if not data:
            continue

        cmd_buffer += data

        placeholder = b"asterisk"
        cmd_buffer = cmd_buffer.replace(b"*\r\n", placeholder)
        cmd_delimiter = b"*"
        for cmd in (cmd_delimiter + cmd for cmd in cmd_buffer.split(cmd_delimiter) if cmd):
            cmd = cmd.replace(placeholder, b"*\r\n")
            print(cmd)
            if is_full_command(cmd):
                print("yes")
                parsed_command = parse_redis_command(cmd)
                print(f"{role}: Received command - {parsed_command}")
                process_command(conn=conn, command=parsed_command, raw_cmd=cmd)
            else:
                print("no")
                cmd_buffer = cmd
                break
        else:
            cmd_buffer = bytearray()


def is_full_command(cmd: bytes) -> bool:
    if b"\r\n" not in cmd:
        return False

    commands_array_head = cmd.split(b"\r\n", maxsplit=1)
    elems_count = int(commands_array_head[0][1:])

    command_pattern = rf"(\$\d+\r\n[\w\-\?\*]+\r\n){'{' + str(elems_count) + '}'}".encode("utf-8")
    command = cmd[len(commands_array_head) + 2:]

    return re.match(command_pattern, command)


def parse_redis_command(serialized_command: bytes) -> list[Any]:
    try:
        decoded_command = serialized_command.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(serialized_command)
    commands: list[Any] = decoded_command.strip().split("\r\n")[1:]
    commands = [command for command in commands if command[0] != "$"]

    for i, cmd in enumerate(commands):
        if cmd.upper() in COMMANDS_TOKENS:
            commands[i] = cmd.upper()

        elif cmd.isnumeric() or cmd[1:].isnumeric():
            commands[i] = int(cmd)

    return commands


def ack() -> bytes:
    return f"*3\r\n$8\r\nREPLCONF\r\n$3\r\nACK\r\n${len(str(processed))}\r\n{processed}\r\n".encode("utf-8")


def ok() -> bytes:
    return "+OK\r\n".encode("utf-8")


def full_resync() -> bytes:
    return f"+FULLRESYNC {replication_id} 0\r\n".encode("utf-8")


def ping() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def set_(key: str, value: str, expire: int | None = None) -> bytes:
    expire_time = time.time() + expire / 1000 if expire is not None else None
    storage[key] = Record(value, expire_time)
    return ok()


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


def print_exceptions(func: Callable, exception_baseclass: Type[BaseException]) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exception_baseclass as err:
            traceback.print_exception(err)
            raise

    return wrapper


def start_server(domain: str, port: int) -> None:
    server = socket.create_server((domain, port), reuse_port=True)

    with ThreadPoolExecutor() as pool:
        print(f"{role}: Ready to accept")
        while True:
            conn, _ = server.accept()
            pool.submit(print_exceptions(commands_handler, BaseException), conn)


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
        print(master_conn.recv(1024))

        master_conn.sendall("*3\r\n$8\r\nREPLCONF\r\n$14\r\nlistening-port\r\n$4\r\n6380\r\n".encode("utf-8"))
        print(master_conn.recv(1024))

        master_conn.sendall("*3\r\n$8\r\nREPLCONF\r\n$4\r\ncapa\r\n$6\r\npsync2\r\n".encode("utf-8"))
        print(master_conn.recv(1024))

        master_conn.sendall("*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n".encode("utf-8"))
        print(master_conn.recv(1024))
        print(master_conn.recv(1024))
        threading.Thread(target=print_exceptions(commands_handler, BaseException), args=(master_conn,)).start()

        start_server("localhost", args.port)

    else:
        role = Role.MASTER
        start_server("localhost", args.port)


if __name__ == "__main__":
    main()
