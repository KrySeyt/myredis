import logging

from tests import responses, commands
from tests.client import create_client
from tests.server import ServerManager

logger = logging.getLogger(__name__)


def test_dbfilename_success(server_manager: ServerManager) -> None:
    server = server_manager.start_server(dbfilename="testfile")
    client = create_client(server.domain, server.port)

    client.send(commands.config_get("dbfilename"))

    assert client.recv(1024) == responses.config_param("dbfilename", "testfile")


def test_dbfilename_default(server_manager: ServerManager) -> None:
    server = server_manager.start_server()
    client = create_client(server.domain, server.port)

    client.send(commands.config_get("dbfilename"))

    assert client.recv(1024) == responses.config_param("dbfilename", "snapshot")


def test_dir_success(server_manager: ServerManager) -> None:
    server = server_manager.start_server(dir="testdir")
    client = create_client(server.domain, server.port)

    client.send(commands.config_get("dir"))

    assert client.recv(1024) == responses.config_param("dir", "testdir")


def test_dir_default(server_manager: ServerManager) -> None:
    server = server_manager.start_server()
    client = create_client(server.domain, server.port)

    client.send(commands.config_get("dir"))

    assert client.recv(1024) == responses.config_param("dir", ".")
