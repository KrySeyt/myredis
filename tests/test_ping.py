import socket

from tests.commands import ping
from tests.responses import pong


def test(client: socket.socket) -> None:
    client.send(ping())

    assert client.recv(1024) == pong()
