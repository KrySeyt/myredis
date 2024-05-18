import socket

from myredis.external.commands import ping
from myredis.external.responses import pong


def test(client: socket.socket) -> None:
    client.send(ping())

    assert client.recv(1024) == pong()
