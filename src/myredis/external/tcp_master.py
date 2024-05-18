import socket
from typing import Any

from myasync import Coroutine, send, recv

from myredis.application.gateways.master import MasterGateway
from myredis.domain.key import Key
from myredis.domain.record import Record


class WrongData(ValueError):
    pass


class TCPMaster(MasterGateway):
    def __init__(self, master_conn: socket.socket) -> None:
        self._master_conn = master_conn

    def is_records_valid(self, records: bytes) -> bool:
        if len(records) > 5 and not records.startswith("SYNC%".encode("utf-8")):
            return False

        splitters = records.count("\r\n".encode("utf-8"))

        if splitters != (3 * self.get_records_count(records)) + 1:
            return False

        return True

    def get_records_count(self, records: bytes) -> int:
        return int(records.split("\r\n".encode("utf-8"))[0][5:], 2)

    def parse_value(self, value: bytes) -> Any:
        if value.startswith(":".encode("utf-8")):
            return int(value[1:])

        if value.startswith("+".encode("utf-8")):
            return value[1:].decode("utf-8")

        raise ValueError(value)

    def parse_records(self, records: bytes) -> dict[Key, Record]:
        assert self.is_records_valid(records)

        built_records = {}
        records_data_iter = iter(records.split("\r\n".encode("utf-8"))[1:])
        for _ in range(self.get_records_count(records)):
            key = self.parse_value(next(records_data_iter))
            value = self.parse_value(next(records_data_iter))
            expire = self.parse_value(next(records_data_iter))

            built_records[key] = Record(value, expire)

        return built_records

    def get_records(self) -> Coroutine[dict[Key, Record]]:
        yield from send(
            self._master_conn,
            "*2\r\n$7\r\nREPLICA\r\n$4\r\nSYNC\r\n".encode("utf-8"),
        )

        data = bytearray()
        while True:
            data_part = yield from recv(self._master_conn, 4096)

            if not data_part:
                raise ConnectionResetError

            data += data_part

            if len(data) > 5 and not data.startswith("SYNC%".encode("utf-8")):
                raise WrongData(data)

            if "\r\n".encode("utf-8") not in data:
                continue

            records_count = int(data.split("\r\n".encode("utf-8"))[0][5:], 2)

            splitters = data.count("\r\n".encode("utf-8"))

            if splitters == (3 * records_count) + 1:
                break

            if splitters > (3 * records_count) + 1:
                raise WrongData(data)

        return self.parse_records(data)
