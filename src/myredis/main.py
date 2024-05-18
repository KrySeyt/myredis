import base64
import re
import socket
import time
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import myasync

from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.sync_with_master import SyncWithMaster
from myredis.domain.record import Record
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_master import TCPMaster


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
    # "LISTENING-PORT",
    # "CAPA",
    "EOF",
    # "PSYNC2",
    # "PSYNC",
    "GETACK",
    "WAIT",
    # "FULLRESYNC",
    "CONFIG",
    "REPLICA",
    "SYNC",
}

role: Role | None = None

args = None

replication_id = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
replication_offset = 0
processed = 0
replicas: dict[socket.socket, int] = {}

z = 0

storage: RAMValuesStorage = RAMValuesStorage()


def send(conn: socket.socket, data: bytes) -> myasync.Coroutine[None]:
    yield myasync.Await(conn, myasync.IOType.OUTPUT)
    conn.send(data)


def recv(conn: socket.socket, size: int) -> myasync.Coroutine[bytes]:
    yield myasync.Await(conn, myasync.IOType.INPUT)
    return conn.recv(size)


def resend_to_replicas(command: bytes) -> myasync.Coroutine[None]:
    for replica in replicas:
        yield from send(replica, command)
        replicas[replica] = 1


def process_command(conn: socket.socket, command: list[Any], raw_cmd: bytes) -> myasync.Coroutine[None]:
    global processed
    match command:
        case ["PING"]:
            if role == Role.MASTER:
                print("ping")
                yield from send(conn, ping())

        case ["ECHO", str(value)]:
            if role == Role.MASTER:
                yield from send(conn, echo(value))

        case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
            resend_to_replicas(raw_cmd)
            response = set_(key, value, expire=expire)
            if role == Role.MASTER:
                yield from send(conn, response)

        case ["SET", str(key), str(value) | int(value)]:
            resend_to_replicas(raw_cmd)
            response = set_(key, value)
            if role == Role.MASTER:
                yield from send(conn, response)

        case ["GET", str(key)]:
            yield from send(conn, get(key))

        case ["INFO", "REPLICATION"]:
            yield from send(conn, info())

        case ["REPLICA", "SYNC"]:
            if role == Role.MASTER:
                d = sync_replica()
                yield from send(conn, d)
                replicas[conn] = 0

        case ["REPLCONF", "GETACK", "*"]:
            yield from send(conn, ack())

        case ["WAIT", int(replicas_count), int(timeout)]:
            if role == Role.MASTER:
                v = yield from wait(replicas_count, timeout)
                yield from send(conn, v)

        case ["REPLCONF", "ACK", int(val)]:
            global z
            z += 1

        case ["CONFIG", "GET", str(key)]:
            if role == Role.MASTER:
                yield from send(conn, config_get(key))

        case _:
            print(f"{role}: Unknown command - {command}")
            yield from send(conn, b"+WRONGCOMMAND\r\n")

    processed += len(raw_cmd)


def commands_handler(conn: socket.socket) -> myasync.Coroutine[None]:
    cmd_buffer = bytearray()
    while True:
        yield myasync.Await(conn, myasync.IOType.INPUT)

        data = yield from recv(conn, 1024)

        if not data:
            break

        cmd_buffer += data

        placeholder = b"asterisk"
        cmd_buffer = cmd_buffer.replace(b"*\r\n", placeholder)
        cmd_delimiter = b"*"
        for cmd in (cmd_delimiter + cmd for cmd in cmd_buffer.split(cmd_delimiter) if cmd):
            cmd = cmd.replace(placeholder, b"*\r\n")
            print(cmd)

            if not is_command(cmd):
                print("Not command")
                continue

            if is_full_command(cmd):
                parsed_command = parse_redis_command(cmd)
                print(f"{role}: Received command - {parsed_command}")
                yield from process_command(conn=conn, command=parsed_command, raw_cmd=cmd)

            else:
                print("Command is not full")
                cmd_buffer = bytearray(cmd)
                break

        else:
            cmd_buffer = bytearray()


def is_command(cmd: bytes) -> bool:
    return all((
            cmd,
            cmd.startswith(b"*"),
            not cmd.startswith("SYNC".encode("utf-8"))
    ))


def is_full_command(cmd: bytes) -> bool:
    if b"\r\n" not in cmd:
        return False

    commands_array_head = cmd.split(b"\r\n", maxsplit=1)
    elems_count = int(commands_array_head[0][1:])

    command_pattern = rf"(\$\d+\r\n[\w\-\?\*]+\r\n){'{' + str(elems_count) + '}'}".encode()
    command = cmd[len(commands_array_head) + 2:]

    return bool(re.match(command_pattern, command))


def parse_redis_command(serialized_command: bytes) -> list[Any]:
    decoded_command = serialized_command.decode("utf-8")
    commands: list[Any] = decoded_command.strip().split("\r\n")[1:]
    commands = [command for command in commands if command[0] != "$"]

    for i, cmd in enumerate(commands):
        if cmd.upper() in COMMANDS_TOKENS:
            commands[i] = cmd.upper()

        elif cmd.isnumeric() or cmd[1:].isnumeric():
            commands[i] = int(cmd)

    return commands


def config_get(key) -> bytes:
    val = getattr(args, key)
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(val))}\r\n{val}\r\n".encode()


def wait(replicas_count: int, timeout: int) -> myasync.Coroutine[bytes]:
    global z
    for repl in (repl for repl, i in replicas.items() if i == 1):
        yield from send(repl, b"*3\r\n$8\r\nREPLCONF\r\n$6\r\nGETACK\r\n$1\r\n*\r\n")

    start = time.time()
    while (z + len([repl for repl, i in replicas.items() if i == 0]) < replicas_count) and ((time.time() - start) < timeout / 1000):
        yield from myasync.sleep(0.001)

    d = z + len([repl for repl, i in replicas.items() if i == 0])
    z = 0

    return f":{d}\r\n".encode()


def ack() -> bytes:
    return f"*3\r\n$8\r\nREPLCONF\r\n$3\r\nACK\r\n${len(str(processed))}\r\n{processed}\r\n".encode()


def ok() -> bytes:
    return b"+OK\r\n"


def full_resync() -> bytes:
    return f"+FULLRESYNC {replication_id} 0\r\n".encode()


def sync_replica() -> bytes:
    interactor = SyncReplica(storage)
    records = interactor()
    command = [f"SYNC%{len(records)}\r\n"]
    for key, record in records.items():
        command.append(
            f"+{key}\r\n"
            f"+{record.value}\r\n"
            f":{record.expires if record.expires else -1}\r\n"
        )

    return "".join(command).encode("utf-8")


def ping() -> bytes:
    interactor = Ping()
    value = interactor()
    return f"+{value}\r\n".encode("utf-8")


def set_(key: str, value: object, expire: int | None = None) -> bytes:
    interactor = Set(storage)
    interactor(
        key,
        Record(
            value,
            time.time() + expire / 1000 if expire is not None else None
        )
    )
    return ok()


def get(key: str) -> bytes:
    interactor = Get(storage)
    record = interactor(key)
    value = record.value if record is not None else -1
    return f"+{value}\r\n".encode()


def echo(input_str: str) -> bytes:
    interactor = Echo()
    value = interactor(input_str)
    return f"${len(value)}\r\n{value}\r\n".encode()


def info() -> bytes:
    data = f"role:{role}\r\nmaster_replid:{replication_id}\r\nmaster_repl_offset:{replication_offset}"
    return f"${len(data)}\r\n{data}\r\n".encode()


def get_new_client(server_socket: socket.socket) -> myasync.Coroutine[tuple[socket.socket, str]]:
    yield myasync.Await(server_socket, myasync.IOType.INPUT)
    return server_socket.accept()


def start_server(domain: str, port: int) -> myasync.Coroutine[None]:
    try:
        server = socket.create_server((domain, port))
        print("SERVER STARTED")
    except OSError:
        print("PORT ALREADY IN USE")
        exit(1)

    while True:
        conn, _ = yield from get_new_client(server)
        myasync.create_task(commands_handler(conn))


def connect_to_master(args) -> myasync.Coroutine[None]:
    master_domain, master_port = args.replicaof
    master_port = int(master_port)
    master_conn = socket.create_connection((master_domain, master_port))

    yield from send(master_conn, b"*1\r\n$4\r\nPING\r\n")
    yield from recv(master_conn, 1024)

    sync_interactor = SyncWithMaster(storage, TCPMaster(master_conn))
    sync_interactor()

    myasync.create_task(commands_handler(master_conn))


def main() -> myasync.Coroutine[None]:
    global role
    global args

    arg_parser = ArgumentParser(description="MyRedis")
    arg_parser.add_argument("--port", default=6379, type=int)
    arg_parser.add_argument("--replicaof", nargs=2, type=str)
    arg_parser.add_argument("--dir", type=str)
    arg_parser.add_argument("--dbfilename", type=str)
    args = arg_parser.parse_args()

    if args.replicaof is not None:
        role = Role.SLAVE
        yield from connect_to_master(args)
        yield from start_server("localhost", args.port)

    else:
        role = Role.MASTER
        yield from start_server("localhost", args.port)
