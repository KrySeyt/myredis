import time

from tests import responses, commands
from tests.client import create_client
from tests.server import ServerManager


def test_create_replica_no_data(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    slave = server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    assert slave.port != master.port


def test_create_replica_with_data(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    master_client = create_client(master.domain, master.port)
    master_client.send(commands.set_("foo", "bar"))
    assert master_client.recv(1024) == responses.ok()

    slave = server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")
    assert slave.port != master.port

    replica_client = create_client(slave.domain, slave.port)
    replica_client.send(commands.get("foo"))
    assert replica_client.recv(1024) == responses.get("bar")


def test_set_resend_to_replica(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    slave = server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    assert slave.port != master.port

    master_client = create_client(master.domain, master.port)
    master_client.send(commands.set_("foo", "bar"))
    assert master_client.recv(1024) == responses.ok()

    time.sleep(0.5)

    replica_client = create_client(slave.domain, slave.port)
    replica_client.send(commands.get("foo"))
    assert replica_client.recv(1024) == responses.get("bar")
