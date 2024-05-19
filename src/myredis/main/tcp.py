import socket
from argparse import ArgumentParser

import myasync
from myasync import Coroutine, Event

from myredis.adapters.controllers.ack import Ack
from myredis.adapters.controllers.config_get import GetConfig
from myredis.adapters.controllers.echo import Echo
from myredis.adapters.controllers.get import Get
from myredis.adapters.controllers.ping import Ping
from myredis.adapters.controllers.set import Set
from myredis.adapters.controllers.sync_replica import SyncReplica
from myredis.adapters.controllers.wait import WaitReplicas
from myredis.application.ack import Ack as AckInteractor
from myredis.application.add_replica import AddReplica as AddReplicaInteractor
from myredis.application.echo import Echo as EchoInteractor
from myredis.application.gateways.ping_master import PingMaster
from myredis.application.get import Get as GetInteractor
from myredis.application.get_config import GetConfig as GetConfigInteractor
from myredis.application.ping import Ping as PingInteractor
from myredis.application.set import Set as SetInteractor
from myredis.application.sync_replica import SyncReplica as SyncReplicaInteractor
from myredis.application.sync_with_master import SyncWithMaster
from myredis.application.wait_replicas import WaitReplicas as WaitReplicasInteractor
from myredis.domain.config import AppConfig, Role
from myredis.external.config import Config
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_api.command_processor import CommandProcessor, Controllers
from myredis.external.tcp_api.server import ServerConfig, TCPServer
from myredis.external.tcp_api.temp import conn_to_stop_event
from myredis.external.tcp_master import TCPMaster
from myredis.external.tcp_replicas import TCPReplicasManager


def connect_to_master(server: TCPServer, master_domain: str, master_port: int) -> Coroutine[None]:
    master_port = int(master_port)
    master_conn = socket.create_connection((master_domain, master_port))

    ping_master_interactor = PingMaster(TCPMaster(master_conn))
    yield from ping_master_interactor()

    sync_interactor = SyncWithMaster(RAMValuesStorage(), TCPMaster(master_conn))
    yield from sync_interactor()

    stop = Event()
    myasync.create_task(server.client_handler(master_conn, stop))
    conn_to_stop_event[master_conn] = stop


def main() -> Coroutine[None]:
    arg_parser = ArgumentParser(description="MyRedis")
    arg_parser.add_argument("--port", default=6379, type=int)
    arg_parser.add_argument("--replicaof", nargs=2, type=str)
    arg_parser.add_argument("--dir", type=str)
    arg_parser.add_argument("--dbfilename", type=str)
    args = arg_parser.parse_args()

    cmd_processor = CommandProcessor(
        config=AppConfig(
            role=Role.SLAVE if args.replicaof else Role.MASTER,
        ),
        controllers=Controllers(
            ping=Ping(PingInteractor()),
            echo=Echo(EchoInteractor()),
            set_=Set(SetInteractor(RAMValuesStorage(), TCPReplicasManager())),
            get=Get(GetInteractor(RAMValuesStorage())),
            sync_replica=SyncReplica(AddReplicaInteractor(TCPReplicasManager()), SyncReplicaInteractor(RAMValuesStorage())),
            ack=Ack(AckInteractor()),
            wait=WaitReplicas(WaitReplicasInteractor(TCPReplicasManager())),
            get_config=GetConfig(GetConfigInteractor(Config(args.__dict__))),
        ),
    )

    server = TCPServer(
        command_processor=cmd_processor,
        server_config=ServerConfig(
            domain="localhost",
            port=args.port,
        ),
        app_config=AppConfig(
            role=Role.SLAVE if args.replicaof else Role.MASTER,
        ),
    )

    if args.replicaof is not None:
        yield from connect_to_master(server, args.replicaof[0], int(args.replicaof[1]))

    yield from server.start()


if __name__ == "__main__":
    myasync.run(main())
