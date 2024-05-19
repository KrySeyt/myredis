import socket

from tests import responses, commands


def test_get(client: socket.socket) -> None:
    client.send(commands.set_("foo", 5))
    assert client.recv(1024) == responses.ok()

    client.send(commands.get("foo"))
    assert client.recv(1024) == responses.get("5")
