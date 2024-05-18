import socket

from myasync import Coroutine

from myredis.application.gateways.replicas import Replicas


class AddReplica:
    def __init__(self, replicas: Replicas) -> None:
        self._replicas = replicas

    # TODO: Replace socket with abstraction
    # TODO: Better send file instead of Records
    def __call__(self, replica_conn: socket.socket) -> Coroutine[None]:
        yield from self._replicas.add_replica(replica_conn)
