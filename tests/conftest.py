from collections.abc import Generator

import pytest

from tests.client import Client, create_client
from tests.server import ServerManager


@pytest.fixture(scope="session")
def server_manager() -> Generator[ServerManager, None, None]:
    manager = ServerManager()
    yield manager
    manager.kill_started_servers()


@pytest.fixture()
def _start_server(server_manager: ServerManager) -> None:
    server_manager.start_server(
        port=6379,
    )


@pytest.fixture(autouse=True)
def _kill_servers(server_manager: ServerManager) -> Generator[None, None, None]:
    yield
    server_manager.kill_started_servers()


@pytest.fixture()
def client(_start_server: None) -> Client:
    return create_client("localhost", 6379)
