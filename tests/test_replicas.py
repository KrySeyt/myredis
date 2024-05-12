from tests.server import ServerManager


def test_create_replica(server_manager: ServerManager) -> None:
    master = server_manager.start_server(port=6379)
    slave = server_manager.start_server(port=6380, replicaof=f"{master.domain} {master.port}")

    assert slave.port != master.port
