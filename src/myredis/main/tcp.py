import socket
from argparse import ArgumentParser

import myasync
from myasync import Coroutine

from myredis.adapters.controllers.command_processor import CommandProcessor, Interactors
from myredis.adapters.views import responses
from myredis.application.ack import Ack
from myredis.application.add_replica import AddReplica
from myredis.application.echo import Echo
from myredis.application.gateways.ping_master import PingMaster
from myredis.application.get import Get
from myredis.application.get_config import GetConfig
from myredis.application.ping import Ping
from myredis.application.set import Set
from myredis.application.sync_replica import SyncReplica
from myredis.application.sync_with_master import SyncWithMaster
from myredis.application.wait_replicas import WaitReplicas
from myredis.domain.config import AppConfig, Role
from myredis.external.config import Config
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_api.server import ServerConfig, TCPServer
from myredis.external.tcp_master import TCPMaster
from myredis.external.tcp_replicas import TCPReplicasManager


def connect_to_master(server: TCPServer, master_domain: str, master_port: int) -> Coroutine[None]:
    master_port = int(master_port)
    master_conn = socket.create_connection((master_domain, master_port))

    ping_master_interactor = PingMaster(TCPMaster(master_conn))
    yield from ping_master_interactor()

    sync_interactor = SyncWithMaster(RAMValuesStorage(), TCPMaster(master_conn), lambda: None)
    yield from sync_interactor()

    myasync.create_task(server.client_handler(master_conn))


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
        interactors=Interactors(
            ping=Ping(responses.pong),
            echo=Echo(responses.echo),
            set_=Set(RAMValuesStorage(), TCPReplicasManager(), responses.ok),
            get=Get(RAMValuesStorage(), responses.get),
            add_replica=AddReplica(TCPReplicasManager(), lambda: None),
            sync_replica=SyncReplica(RAMValuesStorage(), responses.records),
            ack=Ack(responses.ack),
            wait=WaitReplicas(TCPReplicasManager(), responses.wait),
            get_config=GetConfig(Config(args.__dict__), responses.config_param),
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
