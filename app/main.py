import socket
from concurrent.futures import ThreadPoolExecutor


def commands_handler(conn: socket.socket) -> None:
    while command := conn.recv(1024):
        match parse_redis_command(command):
            case ["PING"]:
                conn.send(ping())

            case ["ECHO", value]:
                conn.send(echo(value))


def parse_redis_command(serialized_command: bytes) -> list[str]:
    command = serialized_command.decode("utf-8")
    commands = command.strip().split("\r\n")
    cmds = [cmd for cmd in commands if cmd[0] not in ("*", "$")]
    cmds[0] = cmds[0].upper()
    return cmds


def ping() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def echo(value: str) -> bytes:
    return f"${len(value)}\r\n{value}\r\n".encode("utf-8")


def main():
    with ThreadPoolExecutor() as pool:
        while True:
            server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
            conn, _ = server_socket.accept()
            pool.submit(commands_handler, conn)


if __name__ == "__main__":
    main()
