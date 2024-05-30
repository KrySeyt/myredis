import time
from abc import ABC, abstractmethod
from typing import Any

import myasync
from myasync import Coroutine

from myredis.application.ack import Ack
from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.get_config import GetConfigParam
from myredis.application.interfaces.replicas import Replica
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.key import Key
from myredis.domain.record import Record


class WrongCommand(ValueError):
    pass


class BaseCommandProcessor:
    def process_command(self, command: list[Any], replica: Replica | None = None) -> myasync.Coroutine[bytes | None]:
        match command:
            case ["PING"]:
                response = yield from self.ping()
                return response

            case ["ECHO", str(value)]:
                response = yield from self.echo(value)
                return response

            case "SET", str(key), str(value) | int(value), "PX", int(alive):
                response = yield from self.set(key, value, alive)  # type: ignore[arg-type]
                return response

            case ["SET", str(key), str(value) | int(value)]:
                response = yield from self.set(key, value)  # type: ignore[arg-type]
                return response

            case ["GET", str(key)]:
                response = yield from self.get(key)
                return response

            case ["REPLICA", "SYNC"]:
                assert replica
                response = yield from self.replica_sync(replica)
                return response

            case ["REPLCONF", "GETACK"]:
                response = yield from self.replconf_getack()
                return response

            case ["WAIT", int(replicas_count), int(timeout)]:
                response = yield from self.wait_replicas(replicas_count, timeout)
                return response

            case ["CONFIG", "GET", str(key)]:
                response = yield from self.config_get(key)
                return response

            case _:
                print(f"Unknown command - {command}")
                return b"+WRONGCOMMAND\r\n"

    def ping(self) -> Coroutine[bytes | None]:
        yield None
        return None

    def echo(self, value: str) -> Coroutine[bytes | None]:
        yield None
        return None

    def set(self, key: Key, value: str | int, alive: float | None = None) -> Coroutine[bytes | None]:
        yield None
        return None

    def get(self, key: Key) -> Coroutine[bytes | None]:
        yield None
        return None

    def replica_sync(self, replica: Replica) -> Coroutine[bytes | None]:
        yield None
        return None

    def replconf_getack(self) -> Coroutine[bytes | None]:
        yield None
        return None

    def wait_replicas(self, replicas_count: int, timeout: int) -> Coroutine[bytes | None]:
        yield None
        return None

    def config_get(self, key: str) -> Coroutine[bytes | None]:
        yield None
        return None


class MasterCommandProcessor(BaseCommandProcessor):
    def __init__(
            self,
            ping: Ping[bytes | None],
            echo: Echo[bytes | None],
            set_: Set[bytes | None],
            get: Get[bytes | None],
            add_replica: AddReplica[bytes | None],
            sync_replica: SyncReplica[bytes | None],
            wait: WaitReplicas[bytes | None],
            get_config: GetConfigParam[bytes | None],
    ) -> None:
        self._ping = ping
        self._echo = echo
        self._set = set_
        self._get = get
        self._add_replica = add_replica
        self._sync_replica = sync_replica
        self._wait = wait
        self._get_config = get_config

    def ping(self) -> Coroutine[bytes | None]:
        ping_response = yield from self._ping()
        return ping_response

    def echo(self, value: str) -> Coroutine[bytes | None]:
        echo_response = yield from self._echo(value)
        return echo_response

    def set(self, key: Key, value: str | int, alive: float | None = None) -> Coroutine[bytes | None]:
        response = yield from self._set(
            key,
            Record(
                value,
                time.time() + alive / 1000 if alive else None,
            ),
        )
        return response

    def get(self, key: Key) -> Coroutine[bytes | None]:
        get_response = yield from self._get(key)
        return get_response

    def replica_sync(self, replica: Replica) -> Coroutine[bytes | None]:
        yield from self._add_replica(replica)
        d = yield from self._sync_replica()
        return d

    def wait_replicas(self, replicas_count: int, timeout: int) -> Coroutine[bytes | None]:
        v = yield from self._wait(replicas_count, timeout / 1000)
        return v

    def config_get(self, key: str) -> Coroutine[bytes | None]:
        config_value = yield from self._get_config(key)
        return config_value


class ReplicaCommandProcessor(BaseCommandProcessor):
    def __init__(
            self,
            ping: Ping[bytes | None],
            ack: Ack[bytes | None],
    ) -> None:
        self._ping = ping
        self._ack = ack

    def ping(self) -> Coroutine[bytes | None]:
        response = yield from self._ping()
        return response

    def replconf_getack(self) -> Coroutine[bytes | None]:
        response = yield from self._ack()
        return response


class CommandProcessorFactory(ABC):
    @abstractmethod
    def create_master_command_processor(self) -> Coroutine[MasterCommandProcessor]:
        raise NotImplementedError

    @abstractmethod
    def create_replica_command_processor(self) -> Coroutine[ReplicaCommandProcessor]:
        raise NotImplementedError
