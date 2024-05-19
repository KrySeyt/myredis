import socket

from myasync import Event

conn_to_event: dict[socket.socket, Event] = {}
