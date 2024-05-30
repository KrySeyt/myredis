from myasync import Coroutine

from myredis.adapters.controllers.command_processor import (
    CommandProcessorFactory,
    MasterCommandProcessor,
    ReplicaCommandProcessor,
)
from myredis.adapters.views import responses
from myredis.application.ack import Ack
from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.get_config import GetConfigParam
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.key import Key
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_replicas import TCPReplicasManager


class DefaultCommandProcessorFactory(CommandProcessorFactory):
    def __init__(self, config: dict[Key, str | int]) -> None:
        self._config = config

    def create_master_command_processor(self) -> Coroutine[MasterCommandProcessor]:
        yield None

        cmd_processor = MasterCommandProcessor(
            ping=Ping(responses.pong),
            echo=Echo(responses.echo),
            set_=Set(RAMValuesStorage(), TCPReplicasManager(), responses.ok),
            get=Get(RAMValuesStorage(), responses.get),
            add_replica=AddReplica(TCPReplicasManager(), lambda: None),
            sync_replica=SyncReplica(RAMValuesStorage(), responses.records),
            wait=WaitReplicas(TCPReplicasManager(), responses.wait),
            get_config=GetConfigParam(self._config, responses.config_param),
        )

        return cmd_processor

    def create_replica_command_processor(self) -> Coroutine[ReplicaCommandProcessor]:
        yield None

        cmd_processor = ReplicaCommandProcessor(
            ping=Ping(responses.pong),
            ack=Ack(responses.ack),
        )

        return cmd_processor
