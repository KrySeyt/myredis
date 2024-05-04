import select
import socket

from myasync.loop import Selector


class SelectSelector(Selector):
    def select(
            self,
            read_sockets: list[socket.socket],
            write_sockets: list[socket.socket],
    ) -> tuple[
        list[socket.socket],
        list[socket.socket],
    ]:
        ready_read, ready_write, _ = select.select(
            read_sockets,
            write_sockets,
            [],
            0,
        )
        return ready_read, ready_write
