import socket
from concurrent.futures import ThreadPoolExecutor


def commands_handler(conn: socket.socket) -> None:
    while command := conn.recv(1024):
        match parse_redis_command(command):
            case ["PING"]:
                cmd = ping()
                print(cmd)
                conn.send(cmd)

            # case "ECHO", value:
            #     print(value)
            case _:
                print("OTHER")



def parse_redis_command(serialized_command: bytes) -> list[str]:
    command = serialized_command.decode("utf-8")
    commands = command.strip().split("\r\n")
    cmds = [cmd.upper() for cmd in commands if cmd[0] not in ("*", "$")]
    print(cmds)
    return cmds


def ping() -> bytes:
    return "+PONG\r\n".encode("utf-8")


def main():
    with ThreadPoolExecutor() as pool:
        while True:
            server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
            conn, _ = server_socket.accept()
            pool.submit(commands_handler, conn)


if __name__ == "__main__":
    main()
