from myasync import Coroutine

from myredis.adapters import responses
from myredis.application.add_replica import AddReplica as AddReplicaInteractor
from myredis.application.gateways.replicas import Replica
from myredis.application.sync_replica import SyncReplica as SyncReplicaInteractor


class SyncReplica:
    def __init__(
            self,
            add_replica_interactor: AddReplicaInteractor,
            sync_replica_interactor: SyncReplicaInteractor,
    ) -> None:
        self._add_replica = add_replica_interactor
        self._sync_replica = sync_replica_interactor

    def __call__(self, replica: Replica) -> Coroutine[bytes]:
        yield from self._add_replica(replica)

        records = yield from self._sync_replica()
        return responses.records(records)
