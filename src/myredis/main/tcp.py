import socket
from argparse import ArgumentParser

import myasync
from myasync import Coroutine, Event

from myredis.application.gateways.ping_master import PingMaster
from myredis.application.sync_with_master import SyncWithMaster
from myredis.domain.config import AppConfig, Role
from myredis.external.config import Config
from myredis.external.ram_values_storage import RAMValuesStorage
from myredis.external.tcp_api.config_get import ConfigVar
from myredis.external.tcp_api.server import ServerConfig, TCPServer
from myredis.external.tcp_api.temp import conn_to_stop_event
from myredis.external.tcp_master import TCPMaster


def connect_to_master(server: TCPServer, args) -> Coroutine[None]:
    master_domain, master_port = args.replicaof
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
    ConfigVar.set(Config(args.__dict__))

    server = TCPServer(
        server_config=ServerConfig(
            domain="localhost",
            port=args.port,
        ),
        app_config=AppConfig(
            role=Role.SLAVE if args.replicaof else Role.MASTER,
        ),
    )

    if args.replicaof is not None:
        yield from connect_to_master(server, args)

    yield from server.start()


if __name__ == "__main__":
    myasync.run(main())
