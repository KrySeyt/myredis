import socket

from tests import commands
from tests import responses


def test(client: socket.socket) -> None:
    client.send(commands.ping())

    assert client.recv(1024) == responses.pong()
