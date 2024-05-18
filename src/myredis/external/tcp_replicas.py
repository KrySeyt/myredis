import socket
import time

from myasync import Coroutine, Event, create_task, recv, send, sleep

from myredis.application.gateways.replicas import Replica, ReplicaSentWrongDataError, ReplicasManager

replicas: list[Replica] = []


class TCPReplica(Replica):
    def __init__(self, socket_: socket.socket) -> None:
        self._socket = socket_

    def send(self, bytes_: bytes) -> Coroutine[None]:
        yield from send(self._socket, bytes_)

    def recv(self, bytes_count: int) -> Coroutine[bytes]:
        data = yield from recv(self._socket, bytes_count)
        return data


class TCPReplicasManager(ReplicasManager):
    def __init__(self) -> None:
        self._responded_replicas_count = 0

    def wait_replica(self, replica: Replica, is_timeout: Event) -> Coroutine[None]:
        yield from replica.send(
            b"*3\r\n$8\r\nREPLCONF\r\n$6\r\nGETACK\r\n$1\r\n*\r\n",
        )

        data = bytearray()
        excepted_splitters_count = 7
        while not is_timeout:
            data_part = yield from replica.recv(4096)

            if not data_part:
                raise ConnectionResetError

            data += data_part

            splitters_count = data.count(b"\r\n")

            if splitters_count > excepted_splitters_count:
                raise ReplicaSentWrongDataError(data)

            if splitters_count == excepted_splitters_count:
                self._responded_replicas_count += 1
                break

    def wait(self, replicas_count: int, timeout: float) -> Coroutine[int]:
        is_timeout = Event()
        for repl in replicas:
            create_task(self.wait_replica(repl, is_timeout))

        start = time.time()
        while self._responded_replicas_count < replicas_count and (time.time() - start) <= timeout:
            yield from sleep(0.001)

        is_timeout.set()

        count = self._responded_replicas_count
        self._responded_replicas_count = 0
        return count

    def add_replica(self, replica: Replica) -> Coroutine[None]:
        yield None

        replicas.append(replica)
