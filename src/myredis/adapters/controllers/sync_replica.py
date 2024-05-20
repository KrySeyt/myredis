from collections.abc import Callable
from typing import Generic, TypeVar

from myasync import Coroutine

from myredis.application.add_replica import AddReplica as AddReplicaInteractor
from myredis.application.gateways.replicas import Replica
from myredis.application.sync_replica import SyncReplica as SyncReplicaInteractor
from myredis.domain.record import Record

T_co = TypeVar("T_co", covariant=True)


class SyncReplica(Generic[T_co]):
    def __init__(
            self,
            add_replica_interactor: AddReplicaInteractor,
            sync_replica_interactor: SyncReplicaInteractor,
            presenter: Callable[[dict[str, Record]], T_co],
    ) -> None:
        self._add_replica = add_replica_interactor
        self._sync_replica = sync_replica_interactor
        self._presenter = presenter

    def __call__(self, replica: Replica) -> Coroutine[T_co]:
        yield from self._add_replica(replica)

        records = yield from self._sync_replica()
        return self._presenter(records)
