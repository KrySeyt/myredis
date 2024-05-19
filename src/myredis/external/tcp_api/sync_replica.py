import socket

from myasync import Coroutine

from myredis.application.add_replica import AddReplica
from myredis.application.sync_replica import SyncReplica
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_api.temp import conn_to_stop_event
from myredis.external.tcp_replicas import TCPReplica, TCPReplicasManager


def sync_replica(replica_conn: socket.socket) -> Coroutine[bytes]:
    event = conn_to_stop_event[replica_conn]
    event.set()

    add_replica_interactor = AddReplica(TCPReplicasManager())
    yield from add_replica_interactor(TCPReplica(replica_conn))

    sync_replica_interactor = SyncReplica(RAMValuesStorage())
    records = yield from sync_replica_interactor()
    command = [f"SYNC%{len(records)}\r\n"]
    for key, record in records.items():
        command.append(
            f"+{key}\r\n"
            f"+{record.value}\r\n"
            f":{record.expires if record.expires else -1}\r\n",
        )

    return "".join(command).encode("utf-8")
