import socket
from typing import Any

import myasync
from myasync import send

from myredis.domain.config import AppConfig, Role
from myredis.external.tcp_api.ack import ack
from myredis.external.tcp_api.config_get import config_get
from myredis.external.tcp_api.echo import echo
from myredis.external.tcp_api.get import get
from myredis.external.tcp_api.ping import ping
from myredis.external.tcp_api.set import set_
from myredis.external.tcp_api.sync_replica import sync_replica
from myredis.external.tcp_api.wait import wait


class WrongCommand(ValueError):
    pass


class CommandProcessor:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def process_command(self, conn: socket.socket, command: list[Any]) -> myasync.Coroutine[None]:
        match command:
            case ["PING"]:
                if self._config.role == Role.MASTER:
                    ping_response = yield from ping()
                    yield from send(conn, ping_response)

            case ["ECHO", str(value)]:
                if self._config.role == Role.MASTER:
                    echo_response = yield from echo(value)
                    yield from send(conn, echo_response)

            case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
                response = yield from set_(key, value, expire=expire)
                if self._config.role == Role.MASTER:
                    yield from send(conn, response)

            case ["SET", str(key), str(value) | int(value)]:
                response = yield from set_(key, value)
                if self._config.role == Role.MASTER:
                    yield from send(conn, response)

            case ["GET", str(key)]:
                get_response = yield from get(key)
                yield from send(conn, get_response)

            case ["REPLICA", "SYNC"]:
                if self._config.role == Role.MASTER:
                    d = yield from sync_replica(conn)
                    yield from send(conn, d)

            case ["REPLCONF", "GETACK"]:
                ack_response = yield from ack()
                yield from send(conn, ack_response)

            case ["WAIT", int(replicas_count), int(timeout)]:
                if self._config.role == Role.MASTER:
                    v = yield from wait(replicas_count, timeout)
                    yield from send(conn, v)

            case ["CONFIG", "GET", str(key)]:
                if self._config.role == Role.MASTER:
                    config_value = yield from config_get(key)
                    yield from send(conn, config_value)

            case _:
                print(f"{self._config.role}: Unknown command - {command}")
                yield from send(conn, b"+WRONGCOMMAND\r\n")
