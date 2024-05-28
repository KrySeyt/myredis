from myasync import Coroutine

from myredis.adapters.controllers.command_processor import CommandProcessor, CommandProcessorFactory, Interactors
from myredis.adapters.views import responses
from myredis.application.ack import Ack
from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.get import Get
from myredis.application.get_config import GetConfig
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.config import AppConfig, Role
from myredis.external.config import Config
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_replicas import TCPReplicasManager


class DefaultCommandProcessorFactory(CommandProcessorFactory):
    def __init__(self, is_replica: bool, config: Config) -> None:
        self._is_replica = is_replica
        self._config = config

    def create_command_processor(self) -> Coroutine[CommandProcessor]:
        yield None

        cmd_processor = CommandProcessor(
            config=AppConfig(
                role=Role.SLAVE if self._is_replica else Role.MASTER,
            ),
            interactors=Interactors(
                ping=Ping(responses.pong),
                echo=Echo(responses.echo),
                set_=Set(RAMValuesStorage(), TCPReplicasManager(), responses.ok),
                get=Get(RAMValuesStorage(), responses.get),
                add_replica=AddReplica(TCPReplicasManager(), lambda: None),
                sync_replica=SyncReplica(RAMValuesStorage(), responses.records),
                ack=Ack(responses.ack),
                wait=WaitReplicas(TCPReplicasManager(), responses.wait),
                get_config=GetConfig(self._config, responses.config_param),
            ),
        )

        return cmd_processor
