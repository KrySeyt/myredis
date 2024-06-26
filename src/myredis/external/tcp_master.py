import socket
from typing import Any

from myasync import Coroutine, recv, send

from myredis.adapters.views import commands, responses
from myredis.application.interfaces.master import Master, MasterSentWrongDataError
from myredis.domain.key import Key
from myredis.domain.record import Record


class TCPMaster(Master):
    def __init__(self, master_conn: socket.socket) -> None:
        self._master_conn = master_conn

    def is_records_valid(self, records: bytes) -> bool:
        records_identifier = b"SYNC%"
        if len(records) > len(records_identifier) and not records.startswith(records_identifier):
            return False

        splitters = records.count(b"\r\n")

        if splitters != (3 * self.get_records_count(records)) + 1:
            return False

        return True

    def get_records_count(self, records: bytes) -> int:
        return int(records.split(b"\r\n")[0][5:].decode("utf-8"))

    def parse_value(self, value: bytes) -> Any:
        if value.startswith(b":"):
            return int(value[1:])

        if value.startswith(b"+"):
            return value[1:].decode("utf-8")

        raise ValueError(value)

    def parse_records(self, records: bytes) -> dict[Key, Record[Any]]:
        assert self.is_records_valid(records)

        built_records = {}
        records_data_iter = iter(records.split(b"\r\n")[1:])
        for _ in range(self.get_records_count(records)):
            key = self.parse_value(next(records_data_iter))
            value = self.parse_value(next(records_data_iter))
            expire = self.parse_value(next(records_data_iter))
            expire = None if expire == -1 else expire

            built_records[key] = Record(value, expire)

        return built_records

    def get_records(self) -> Coroutine[dict[Key, Record[Any]]]:
        yield from send(
            self._master_conn,
            commands.replica_sync(),
        )

        data = bytearray()
        while True:
            data_part = yield from recv(self._master_conn, 4096)

            if not data_part:
                raise ConnectionResetError

            data += data_part

            records_identifier = b"SYNC%"
            if len(data) > len(records_identifier) and not data.startswith(records_identifier):
                raise MasterSentWrongDataError(data)

            if b"\r\n" not in data:
                continue

            records_count = self.get_records_count(data)

            splitters = data.count(b"\r\n")

            if splitters == (3 * records_count) + 1:
                break

            if splitters > (3 * records_count) + 1:
                raise MasterSentWrongDataError(data)

        return self.parse_records(data)

    def ping(self) -> Coroutine[str]:
        yield from send(self._master_conn, commands.ping())

        data = bytearray()
        while data != responses.pong():
            data_part = yield from recv(self._master_conn, 4096)

            if not data_part:
                raise ConnectionResetError

            data += data_part

            if not responses.pong().startswith(data):
                raise MasterSentWrongDataError(data)

        value = self.parse_value(data)
        assert isinstance(value, str)
        return value
