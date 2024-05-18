from myredis.external import responses, commands
from tests.client import create_client
from tests.server import ServerManager


def test_wait_with_forwarded_data(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    client = create_client(master.domain, master.port)
    client.send(commands.set_("key", "value"))

    assert client.recv(1024) == responses.ok()

    client.send(commands.wait(1, 1000))

    assert client.recv(1024, 3) == responses.wait(1)


def test_wait_expect_exact_replicas(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    client = create_client(master.domain, master.port)
    client.send(commands.wait(1, 99999999))

    assert client.recv(1024, 3) == responses.wait(1)


def test_wait_expect_less_replicas(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")
    server_manager.start_server(port=6381, replicaof=f"{master.domain} {master.port}")

    client = create_client(master.domain, master.port)
    client.send(commands.wait(1, 99999999))

    assert client.recv(1024, 3) in (responses.wait(1), responses.wait(2))


def test_wait_expect_more_replicas(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    client = create_client(master.domain, master.port)
    client.send(commands.wait(3, 500))

    assert client.recv(1024, 3) == responses.wait(1)
