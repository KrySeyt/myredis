import logging
import re
import socket
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import myasync
from myasync import Coroutine, recv, send

from myredis.adapters.controllers.command_processor import BaseCommandProcessor
from myredis.external.tcp_replicas import TCPReplica

logger = logging.getLogger(__name__)

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
    def __init__(
            self,
            command_processor_factory: Callable[[], Coroutine[BaseCommandProcessor]],
            server_config: ServerConfig,
    ) -> None:
        self._server_config = server_config
        self._command_processor_factory = command_processor_factory

    def start(self) -> Coroutine[None]:
        try:
            server = socket.create_server((
                self._server_config.domain,
                self._server_config.port,
            ))
            logger.info("SERVER STARTED")
        except OSError:
            logger.error("PORT ALREADY IN USE")
            exit(1)

        while True:
            conn, _ = yield from self.get_new_client(server)
            myasync.create_task(self.client_handler(conn))

    def client_handler(self, conn: socket.socket) -> myasync.Coroutine[None]:
        command_processor = yield from self._command_processor_factory()
        cmd_buffer = bytearray()
        pooling = True
        while pooling:
            try:
                data = yield from recv(conn, 1024)
            except ConnectionResetError:
                return

            if not data:
                break

            cmd_buffer += data

            placeholder = b"asterisk"
            cmd_buffer = cmd_buffer.replace(b"*\r\n", placeholder)
            cmd_delimiter = b"*"
            for cmd in (cmd_delimiter + cmd for cmd in cmd_buffer.split(cmd_delimiter) if cmd):
                cmd = cmd.replace(placeholder, b"*\r\n")

                if not self.is_command(cmd):
                    continue

                if self.is_full_command(cmd):
                    parsed_command = self.parse_command(cmd)
                    logger.info(f"Received command - {parsed_command}")
                    response = yield from command_processor.process_command(
                        command=parsed_command,
                        replica=TCPReplica(conn),
                    )

                    if response is not None:
                        yield from send(conn, response)

                    if parsed_command == ["REPLICA", "SYNC"]:
                        return

                else:
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

        command_pattern = rf"(\$\d+\r\n.+\r\n){'{' + str(elems_count) + '}'}".encode()
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
