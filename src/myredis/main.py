import re
import socket
import time
from argparse import ArgumentParser
from enum import StrEnum
from typing import Any

import myasync
from myasync import Coroutine, recv, send, Event

from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.sync_with_master import SyncWithMaster
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.record import Record
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_master import TCPMaster
from myredis.external.tcp_replicas import TCPReplicas


class Role(StrEnum):
    MASTER = "master"
    SLAVE = "slave"


conn_to_event = {}


COMMANDS_TOKENS = {
    "PING",
    "ECHO",
    "SET",
    "PX",
    "GET",
    "INFO",
    "REPLICATION",
    "REPLCONF",
    "EOF",
    "GETACK",
    "WAIT",
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

storage: RAMValuesStorage = RAMValuesStorage()


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
                ping_response = yield from ping()
                yield from send(conn, ping_response)

        case ["ECHO", str(value)]:
            if role == Role.MASTER:
                echo_response = yield from echo(value)
                yield from send(conn, echo_response)

        case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
            resend_to_replicas(raw_cmd)
            response = yield from set_(key, value, expire=expire)
            if role == Role.MASTER:
                yield from send(conn, response)

        case ["SET", str(key), str(value) | int(value)]:
            resend_to_replicas(raw_cmd)
            response = yield from set_(key, value)
            if role == Role.MASTER:
                yield from send(conn, response)

        case ["GET", str(key)]:
            get_response = yield from get(key)
            yield from send(conn, get_response)

        case ["INFO", "REPLICATION"]:
            yield from send(conn, info())

        case ["REPLICA", "SYNC"]:
            if role == Role.MASTER:
                d = yield from sync_replica(conn)
                yield from send(conn, d)
                replicas[conn] = 0

        case ["REPLCONF", "GETACK", "*"]:
            yield from send(conn, ack())

        case ["WAIT", int(replicas_count), int(timeout)]:
            if role == Role.MASTER:
                v = yield from wait(replicas_count, timeout)
                yield from send(conn, v)

        case ["CONFIG", "GET", str(key)]:
            if role == Role.MASTER:
                yield from send(conn, config_get(key))

        case _:
            print(f"{role}: Unknown command - {command}")
            yield from send(conn, b"+WRONGCOMMAND\r\n")

    processed += len(raw_cmd)


def commands_handler(conn: socket.socket, event: Event) -> myasync.Coroutine[None]:
    cmd_buffer = bytearray()
    while not event:
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
    wait_interactor = WaitReplicas(TCPReplicas())
    responded_replicas_count = yield from wait_interactor(replicas_count, timeout / 1000)
    return f":{responded_replicas_count}\r\n".encode()


def ack() -> bytes:
    return f"*3\r\n$8\r\nREPLCONF\r\n$3\r\nACK\r\n${len(str(processed))}\r\n{processed}\r\n".encode()


def ok() -> bytes:
    return b"+OK\r\n"


def full_resync() -> bytes:
    return f"+FULLRESYNC {replication_id} 0\r\n".encode()


def sync_replica(replica_conn: socket.socket) -> Coroutine[bytes]:
    event = conn_to_event[replica_conn]
    event.set()

    add_replica_interactor = AddReplica(TCPReplicas())
    yield from add_replica_interactor(replica_conn)

    sync_replica_interactor = SyncReplica(storage)
    records = yield from sync_replica_interactor()
    command = [f"SYNC%{len(records)}\r\n"]
    for key, record in records.items():
        command.append(
            f"+{key}\r\n"
            f"+{record.value}\r\n"
            f":{record.expires if record.expires else -1}\r\n"
        )

    return "".join(command).encode("utf-8")


def ping() -> Coroutine[bytes]:
    interactor = Ping()
    value = yield from interactor()
    return f"+{value}\r\n".encode("utf-8")


def set_(key: str, value: object, expire: int | None = None) -> Coroutine[bytes]:
    interactor = Set(storage)
    yield from interactor(
        key,
        Record(
            value,
            time.time() + expire / 1000 if expire is not None else None
        )
    )
    return ok()


def get(key: str) -> Coroutine[bytes]:
    interactor = Get(storage)
    record = yield from interactor(key)
    value = record.value if record is not None else -1
    return f"+{value}\r\n".encode()


def echo(input_str: str) -> Coroutine[bytes]:
    interactor = Echo()
    value = yield from interactor(input_str)
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
        event = Event()
        myasync.create_task(commands_handler(conn, event))
        conn_to_event[conn] = event


def connect_to_master(args) -> Coroutine[None]:
    master_domain, master_port = args.replicaof
    master_port = int(master_port)
    master_conn = socket.create_connection((master_domain, master_port))

    yield from send(master_conn, b"*1\r\n$4\r\nPING\r\n")
    yield from recv(master_conn, 1024)

    sync_interactor = SyncWithMaster(storage, TCPMaster(master_conn))
    yield from sync_interactor()

    event = Event()
    myasync.create_task(commands_handler(master_conn, event))
    conn_to_event[master_conn] = event


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
