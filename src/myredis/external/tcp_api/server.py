import re
import socket
from dataclasses import dataclass
from typing import Any

import myasync
from myasync import Coroutine, Event, recv, send

from myredis.domain.config import AppConfig
from myredis.external.tcp_api.command_processor import CommandProcessor
from myredis.external.tcp_api.temp import conn_to_stop_event

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


@dataclass
class ServerConfig:
    domain: str
    port: int


class TCPServer:
    def __init__(self, command_processor: CommandProcessor, app_config: AppConfig, server_config: ServerConfig) -> None:
        self._app_config = app_config
        self._server_config = server_config
        self._command_processor = command_processor

    def start(self) -> Coroutine[None]:
        try:
            server = socket.create_server((
                self._server_config.domain,
                self._server_config.port,
            ))
            print("SERVER STARTED")
        except OSError:
            print("PORT ALREADY IN USE")
            exit(1)

        while True:
            conn, _ = yield from self.get_new_client(server)
            event = Event()
            myasync.create_task(self.client_handler(conn, event))
            conn_to_stop_event[conn] = event

    def client_handler(self, conn: socket.socket, stop: Event) -> myasync.Coroutine[None]:
        cmd_buffer = bytearray()
        while not stop:
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

                if not self.is_command(cmd):
                    print("Not command")
                    continue

                if self.is_full_command(cmd):
                    parsed_command = self.parse_command(cmd)
                    print(f"{self._app_config.role}: Received command - {parsed_command}")
                    response = yield from self._command_processor.process_command(command=parsed_command, conn=conn)
                    if response is not None:
                        yield from send(conn, response)

                else:
                    print("Command is not full")
                    cmd_buffer = bytearray(cmd)
                    break

            else:
                cmd_buffer = bytearray()

    def get_new_client(self, server_socket: socket.socket) -> myasync.Coroutine[tuple[socket.socket, str]]:
        yield myasync.Await(server_socket, myasync.IOType.INPUT)
        return server_socket.accept()

    def is_command(self, cmd: bytes) -> bool:
        return all((
            cmd,
            cmd.startswith(b"*"),
            not cmd.startswith(b"SYNC"),
        ))

    def is_full_command(self, cmd: bytes) -> bool:
        if b"\r\n" not in cmd:
            return False

        commands_array_head = cmd.split(b"\r\n", maxsplit=1)
        elems_count = int(commands_array_head[0][1:])

        command_pattern = rf"(\$\d+\r\n[\w\-\?\*]+\r\n){'{' + str(elems_count) + '}'}".encode()
        command = cmd[len(commands_array_head) + 2:]

        return bool(re.match(command_pattern, command))

    def parse_command(self, serialized_command: bytes) -> list[Any]:
        decoded_command = serialized_command.decode("utf-8")
        commands: list[Any] = decoded_command.strip().split("\r\n")[1:]
        commands = [command for command in commands if command[0] != "$"]

        for i, cmd in enumerate(commands):
            if cmd.upper() in COMMANDS_TOKENS:
                commands[i] = cmd.upper()

            elif cmd.isnumeric() or cmd[1:].isnumeric():
                commands[i] = int(cmd)

        return commands
