import logging
import select
import socket
import time

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, socket_: socket.socket) -> None:
        self.socket = socket_

    def recv(self, bytes_: int, timeout: float | None = None) -> bytes:
        read_ready_socks, _, _ = select.select(
            [self.socket],
            [],
            [],
            timeout if timeout is not None else None,
        )

        if not read_ready_socks:
            raise TimeoutError

        return self.socket.recv(bytes_)

    def send(self, bytes_: bytes) -> int:
        return self.socket.send(bytes_)


def create_client(domain: str, port: int, attempts: int = 1) -> Client:
    assert attempts >= 1

    attempt = 1
    while True:
        try:
            logger.info(domain, port)
            return Client(socket.create_connection((domain, port)))
        except ConnectionRefusedError:
            if attempt > attempts:
                raise

            attempt += 1
            time.sleep(0.5)
