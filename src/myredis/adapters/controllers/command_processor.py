import time
from dataclasses import dataclass
from typing import Any

import myasync

from myredis.application.ack import Ack
from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.get_config import GetConfig
from myredis.application.interfaces.replicas import Replica
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.config import AppConfig, Role
from myredis.domain.record import Record


class WrongCommand(ValueError):
    pass


@dataclass
class Interactors:
    ping: Ping[bytes | None]
    echo: Echo[bytes | None]
    set_: Set[bytes | None]
    get: Get[bytes | None]
    add_replica: AddReplica[bytes | None]
    sync_replica: SyncReplica[bytes | None]
    ack: Ack[bytes | None]
    wait: WaitReplicas[bytes | None]
    get_config: GetConfig[bytes | None]


class CommandProcessor:
    def __init__(self, config: AppConfig, interactors: Interactors) -> None:
        self._config = config
        self._interactors = interactors

    def process_command(self, command: list[Any], replica: Replica | None = None) -> myasync.Coroutine[bytes | None]:
        match command:
            case ["PING"]:
                ping_response = yield from self._interactors.ping()
                return ping_response

            case ["ECHO", str(value)]:
                if self._config.role == Role.MASTER:
                    echo_response = yield from self._interactors.echo(value)
                    return echo_response

            case ["SET", str(key), str(value) | int(value), "PX", int(expire)]:
                response = yield from self._interactors.set_(
                    key,
                    Record(
                        value,
                        time.time() + expire / 1000,
                    ),
                )
                if self._config.role == Role.MASTER:
                    return response

            case ["SET", str(key), str(value) | int(value)]:
                response = yield from self._interactors.set_(
                    key,
                    Record(
                        value,
                    ),
                )
                if self._config.role == Role.MASTER:
                    return response

            case ["GET", str(key)]:
                get_response = yield from self._interactors.get(key)
                return get_response

            case ["REPLICA", "SYNC"]:
                if self._config.role == Role.MASTER:
                    assert replica
                    yield from self._interactors.add_replica(replica)
                    d = yield from self._interactors.sync_replica()
                    return d

            case ["REPLCONF", "GETACK"]:
                ack_response = yield from self._interactors.ack()
                return ack_response

            case ["WAIT", int(replicas_count), int(timeout)]:
                if self._config.role == Role.MASTER:
                    v = yield from self._interactors.wait(replicas_count, timeout / 1000)
                    return v

            case ["CONFIG", "GET", str(key)]:
                if self._config.role == Role.MASTER:
                    config_value = yield from self._interactors.get_config(key)
                    return config_value

            case _:
                print(f"{self._config.role}: Unknown command - {command}")
                return b"+WRONGCOMMAND\r\n"

        return None
