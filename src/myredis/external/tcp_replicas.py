import socket
import time

from myasync import Coroutine, Event, send, recv, sleep, create_task

from myredis.application.gateways.replicas import Replicas, ReplicaSentWrongData

replicas: list[socket.socket] = []


class TCPReplicas(Replicas):
    def __init__(self) -> None:
        self._responded_replicas_count = 0

    def wait_replica(self, replica_conn: socket.socket, is_timeout: Event) -> Coroutine[None]:
        yield from send(
            replica_conn,
            "*3\r\n$8\r\nREPLCONF\r\n$6\r\nGETACK\r\n$1\r\n*\r\n".encode("utf-8"),
        )

        data = bytearray()
        excepted_splitters_count = 7
        while not is_timeout:
            data_part = yield from recv(replica_conn, 4096)

            if not data_part:
                raise ConnectionResetError

            data += data_part

            splitters_count = data.count("\r\n".encode("utf-8"))

            if splitters_count > excepted_splitters_count:
                raise ReplicaSentWrongData(data)

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

    def add_replica(self, replica_conn: socket.socket) -> Coroutine[None]:
        yield None

        replicas.append(replica_conn)
