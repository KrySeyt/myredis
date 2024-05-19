import re
import socket
from argparse import ArgumentParser
from typing import Any

import myasync
from myasync import Coroutine, Event, recv, send

from myredis.application.sync_with_master import SyncWithMaster
from myredis.domain.config import Config, Role
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_api.command_parser import CommandProcessor
from myredis.external.tcp_api.conn_to_event import conn_to_event
from myredis.external.tcp_master import TCPMaster


COMMANDS_TOKENS = {
    "PING",
    "ECHO",
    "SET",
    "PX",
    "GET",
    "REPLCONF",
    "EOF",
    "GETACK",
    "WAIT",
    "CONFIG",
    "REPLICA",
    "SYNC",
}

args = None

replication_offset = 0

config = None


def commands_handler(conn: socket.socket, event: Event) -> myasync.Coroutine[None]:
    cmd_processor = CommandProcessor(config)
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
                print(f"{config.role}: Received command - {parsed_command}")
                yield from cmd_processor.process_command(conn=conn, command=parsed_command, args=args)

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
            not cmd.startswith(b"SYNC"),
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

    sync_interactor = SyncWithMaster(RAMValuesStorage(), TCPMaster(master_conn))
    yield from sync_interactor()

    event = Event()
    myasync.create_task(commands_handler(master_conn, event))
    conn_to_event[master_conn] = event


def main() -> myasync.Coroutine[None]:
    global role
    global args
    global config

    arg_parser = ArgumentParser(description="MyRedis")
    arg_parser.add_argument("--port", default=6379, type=int)
    arg_parser.add_argument("--replicaof", nargs=2, type=str)
    arg_parser.add_argument("--dir", type=str)
    arg_parser.add_argument("--dbfilename", type=str)
    args = arg_parser.parse_args()

    if args.replicaof is not None:
        config = Config(role=Role.SLAVE)
        yield from connect_to_master(args)
        yield from start_server("localhost", args.port)

    else:
        config = Config(role=Role.MASTER)
        yield from start_server("localhost", args.port)
