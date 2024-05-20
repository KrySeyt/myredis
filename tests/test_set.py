import socket
import time

from tests import responses, commands


def test(client: socket.socket) -> None:
    client.send(commands.set_("foo", 5))
    assert client.recv(1024) == responses.ok()

    client.send(commands.get("foo"))
    assert client.recv(1024) == responses.get(5)


def test_expire_success(client: socket.socket) -> None:
    client.send(commands.set_("expire-success", 5, 3000))
    assert client.recv(1024) == responses.ok()

    time.sleep(1)

    client.send(commands.get("expire-success"))
    assert client.recv(1024) == responses.get(5)


def test_expire_fail(client: socket.socket) -> None:
    client.send(commands.set_("expire-fail", 5, 500))
    assert client.recv(1024) == responses.ok()
    time.sleep(1)

    client.send(commands.get("expire-fail"))
    assert client.recv(1024) == responses.not_found()
