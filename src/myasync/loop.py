from __future__ import annotations

import socket
from abc import ABC, abstractmethod
from collections.abc import Generator
from enum import Enum, auto
from queue import SimpleQueue
from typing import Any, Generic, TypeVar

T_co = TypeVar("T_co", covariant=True)
Coroutine = Generator["Await | None", None, T_co]


class IOType(Enum):
    INPUT = auto()
    OUTPUT = auto()


class Await:
    def __init__(self, sock: socket.socket, io_type: IOType) -> None:
        self.socket = sock
        self.type = io_type


class EventLoop:
    def __init__(self, selector: Selector) -> None:
        self._selector = selector
        self._tasks: SimpleQueue[AbstractTask[Any]] = SimpleQueue()
        self._stopped_read: list[socket.socket] = []
        self._stopped_write: list[socket.socket] = []
        self._sock_to_tasks: dict[socket.socket, list[AbstractTask[Any]]] = {}

    def run(self) -> None:
        while any(
            (
                not self._tasks.empty(),
                self._stopped_read,
                self._stopped_write,
            ),
        ):
            wait_tasks = []
            while not self._tasks.empty():
                task = self._tasks.get_nowait()

                try:
                    await_ = next(task)
                except StopIteration:
                    continue

                if await_ is None:
                    wait_tasks.append(task)
                    continue

                sock = await_.socket
                self._sock_to_tasks.setdefault(sock, []).append(task)
                if await_.type == IOType.INPUT:
                    self._stopped_read.append(sock)

                elif await_.type == IOType.OUTPUT:
                    self._stopped_write.append(sock)

            ready_read, ready_write = self._selector.select(
                self._stopped_read,
                self._stopped_write,
            )

            for sock in ready_read:
                for t in self._sock_to_tasks.pop(sock):
                    self._tasks.put_nowait(t)
                self._stopped_read.remove(sock)

            for sock in ready_write:
                for t in self._sock_to_tasks.pop(sock):
                    self._tasks.put_nowait(t)
                self._stopped_write.remove(sock)

            for t in wait_tasks:
                self._tasks.put_nowait(t)

    def attach_task(self, task: AbstractTask[T_co]) -> None:
        self._tasks.put_nowait(task)


class Selector(ABC):
    @abstractmethod
    def select(
            self,
            read_sockets: list[socket.socket],
            write_sockets: list[socket.socket],
    ) -> tuple[
        list[socket.socket],
        list[socket.socket],
    ]:
        raise NotImplementedError


class AbstractTask(ABC, Generic[T_co]):
    @property
    @abstractmethod
    def is_completed(self) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def result(self) -> T_co | None:
        raise NotImplementedError

    def __iter__(self) -> AbstractTask[T_co]:
        return self

    @abstractmethod
    def __next__(self) -> Await | None:
        raise NotImplementedError
