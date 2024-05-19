import logging
import subprocess
from dataclasses import dataclass
from typing import Any

from myredis.adapters import commands, responses
from tests.client import create_client

logger = logging.getLogger(__name__)


class WrongServerResponseError(ValueError):
    pass


class WrongServerPIDError(Exception):
    pass


class ServerUnavailableError(Exception):
    pass


class ServerExitError(ServerUnavailableError):
    pass


class ServerExitWithErrorError(ServerUnavailableError):
    pass


class PortAlreadyInUseError(ServerExitWithErrorError):
    pass


PID = int


@dataclass(frozen=True)
class Server:
    process: subprocess.Popen
    domain: str
    port: int


class ServerManager:
    def __init__(self) -> None:
        self.servers: dict[PID, Server] = {}

    def get_start_command(self, **start_params: Any) -> list[str]:
        start_command = ["python", "-um", "src.myredis"]

        for key, value in start_params.items():
            start_command.append(f"--{key}")
            start_command.extend(str(value).split())

        return start_command

    def ping_server(self, server: Server) -> None:
        conn = create_client(server.domain, server.port, attempts=3)
        conn.send(commands.ping())
        data = bytearray()
        while data != responses.pong():
            recv_data = conn.recv(1024)

            if not recv_data:
                raise ConnectionResetError

            data += recv_data

            if data not in responses.pong():
                raise WrongServerResponseError(data)

    def start_server(self, *, choose_free_port: bool = True, **start_params: Any) -> Server:
        start_command = self.get_start_command(**start_params)
        logger.info(f"Start command: {start_command}")
        proc = subprocess.Popen(start_command, stdout=subprocess.PIPE)

        port = start_params.get("port", None) or 6379

        assert proc.stdout is not None

        server = Server(
            process=proc,
            domain="localhost",
            port=port,
        )

        server_message = proc.stdout.readline().strip().decode("utf-8")
        logger.info(f"Server message: {server_message}")
        if server_message == "PORT ALREADY IN USE":
            if not choose_free_port:
                raise PortAlreadyInUseError

            return self.start_server(choose_free_port=choose_free_port, **{**start_params, "port": port + 1})

        if server_message != "SERVER STARTED":
            raise WrongServerResponseError(server_message)

        if "replicaof" not in start_params:
            self.ping_server(server)

        self.servers[server.process.pid] = server

        return server

    def kill_server(self, server_pid: PID) -> None:
        if server_pid not in self.servers:
            raise WrongServerPIDError

        self.servers.pop(server_pid).process.terminate()

    def kill_started_servers(self) -> None:
        for server in self.servers.values():
            server.process.terminate()

        self.servers.clear()
