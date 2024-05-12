from tests.server import ServerManager


def test_server(server_manager: ServerManager) -> None:
    server1 = server_manager.start_server()
    server2 = server_manager.start_server()

    assert server1.port != server2.port
