import socket

from tests import responses, commands


def test(client: socket.socket) -> None:
    client.send(commands.echo("test_echo"))
    assert client.recv(1024) == responses.echo("test_echo")
