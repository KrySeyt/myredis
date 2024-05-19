import socket
from dataclasses import dataclass
from typing import Any

import myasync

from myredis.adapters.controllers.ack import Ack
from myredis.adapters.controllers.config_get import GetConfig
from myredis.adapters.controllers.echo import Echo
from myredis.adapters.controllers.get import Get
from myredis.adapters.controllers.ping import Ping
from myredis.adapters.controllers.set import Set
from myredis.adapters.controllers.sync_replica import SyncReplica
from myredis.adapters.controllers.wait import WaitReplicas
from myredis.domain.config import AppConfig, Role


class WrongCommand(ValueError):
    pass


@dataclass
class Controllers:
    ping: Ping
    echo: Echo
    set_: Set
    get: Get
    sync_replica: SyncReplica
    ack: Ack
    wait: WaitReplicas
    get_config: GetConfig


class CommandProcessor:
    def __init__(self, config: AppConfig, controllers: Controllers) -> None:
        self._config = config
        self._controllers = controllers

    # TODO: remove socket
    def process_command(self, command: list[Any], conn: socket.socket) -> myasync.Coroutine[bytes | None]:
        match command:
            case ["PING"]:
                ping_response = yield from self._controllers.ping()
                return ping_response

            case ["ECHO", str(value)]:
                if self._config.role == Role.MASTER:
                    echo_response = yield from self._controllers.echo(value)
                    return echo_response

            case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
                response = yield from self._controllers.set_(key, value, expire=expire)
                if self._config.role == Role.MASTER:
                    return response

            case ["SET", str(key), str(value) | int(value)]:
                response = yield from self._controllers.set_(key, value)
                if self._config.role == Role.MASTER:
                    return response

            case ["GET", str(key)]:
                get_response = yield from self._controllers.get(key)
                return get_response

            case ["REPLICA", "SYNC"]:
                if self._config.role == Role.MASTER:
                    d = yield from self._controllers.sync_replica(conn)
                    return d

            case ["REPLCONF", "GETACK"]:
                ack_response = yield from self._controllers.ack()
                return ack_response

            case ["WAIT", int(replicas_count), int(timeout)]:
                if self._config.role == Role.MASTER:
                    v = yield from self._controllers.wait(replicas_count, timeout)
                    return v

            case ["CONFIG", "GET", str(key)]:
                if self._config.role == Role.MASTER:
                    config_value = yield from self._controllers.get_config(key)
                    return config_value

            case _:
                print(f"{self._config.role}: Unknown command - {command}")
                return b"+WRONGCOMMAND\r\n"

        return None
