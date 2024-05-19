import socket

from myasync import Event

conn_to_stop_event: dict[socket.socket, Event] = {}
