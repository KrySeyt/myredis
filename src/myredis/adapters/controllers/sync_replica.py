import socket

from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.add_replica import AddReplica as AddReplicaInteractor
from myredis.application.sync_replica import SyncReplica as SyncReplicaInteractor
from myredis.external.tcp_api.temp import conn_to_stop_event
from myredis.external.tcp_replicas import TCPReplica


class SyncReplica:
    def __init__(
            self,
            add_replica_interactor: AddReplicaInteractor,
            sync_replica_interactor: SyncReplicaInteractor,
    ) -> None:
        self._add_replica = add_replica_interactor
        self._sync_replica = sync_replica_interactor

    # TODO: remove socket + fix temp solution with conn_to_stop_event
    def __call__(self, replica_conn: socket.socket) -> Coroutine[bytes]:
        event = conn_to_stop_event[replica_conn]
        event.set()

        yield from self._add_replica(TCPReplica(replica_conn))

        records = yield from self._sync_replica()
        return responses.records(records)
